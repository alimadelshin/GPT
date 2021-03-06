import torch

from torch.utils.data import Dataset, DataLoader
from torchtext.data.functional import load_sp_model

from util.prepro import CustomDataset, get_samples

import torch.nn.functional as F
import torch.distributed as dist
import torch.multiprocessing as mp
import numpy as np
import os
import argparse
import pickle
import datetime

from GPT2 import model

parser = argparse.ArgumentParser(description='GPT2')
parser.add_argument('--resume', default=None, help='')
parser.add_argument('--batch_size', type=int, default=64, help='')
parser.add_argument('--num_workers', type=int, default=2, help='')
parser.add_argument("--gpu_devices", type=int, nargs='+', default=None, help="")
parser.add_argument('--gpu', default=None, type=int, help='GPU id to use.')
parser.add_argument('--accumulate_steps', default=1, type=int, help='Accumulated steps.')
parser.add_argument('--dist-url', default='tcp://127.0.0.1:3456', type=str, help='')
parser.add_argument('--dist-backend', default='nccl', type=str, help='')
parser.add_argument('--rank', default=0, type=int, help='')
parser.add_argument('--world_size', default=1, type=int, help='')
parser.add_argument('--distributed', action='store_true', help='')
args = parser.parse_args()

gpu_devices = ','.join([str(id) for id in args.gpu_devices])
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_devices

class Schedule:
    def __init__(self, d_model, warmup_steps = 4000):
        self.d_model = torch.tensor(d_model, dtype= torch.float32)
        self.warmup_steps = torch.tensor(warmup_steps, dtype= torch.float32)

    def next_step(self, step):
        step = torch.tensor(step, dtype= torch.float32)

        arg_1 = torch.rsqrt(step)
        arg_2 = step * (self.warmup_steps ** -1.5)

        return torch.rsqrt(self.d_model) *  torch.min(arg_1, arg_2)
        
def main():
    args = parser.parse_args()

    ngpus_per_node = torch.cuda.device_count()

    args.world_size = ngpus_per_node * args.world_size
    mp.spawn(main_worker, nprocs=ngpus_per_node, args=(ngpus_per_node, args))

def main_worker(gpu, ngpus_per_node, args):
    args.gpu = gpu
    ngpus_per_node = torch.cuda.device_count()
    print("Use GPU: {} for training".format(args.gpu))

    args.rank = args.rank * ngpus_per_node + gpu
    dist.init_process_group(backend=args.dist_backend, init_method=args.dist_url,
                            world_size=args.world_size, rank=args.rank)
    
    
    encoder = load_sp_model('util/bpe.model')
    print('Tokenizer loaded..')

    num_layers = 32
    d_model = 1024
    num_heads =  8
    dropout_rate = 0.1

    print('==> Making model..')    
    net = model.GTP2(num_layers = num_layers, d_model = d_model, num_heads = num_heads, vocab_size=len(encoder), rate=dropout_rate)

    for p in net.parameters():
        if p.dim() > 1:
            torch.nn.init.xavier_uniform_(p)

    torch.cuda.set_device(args.gpu)
    net.cuda(args.gpu)

    args.batch_size = int(args.batch_size / ngpus_per_node)
    args.num_workers = int(args.num_workers / ngpus_per_node)
    
    net = torch.nn.parallel.DistributedDataParallel(net, device_ids=[args.gpu])

    num_params = sum(p.numel() for p in net.parameters() if p.requires_grad)
    print('The number of parameters of model is', num_params)
    
    scheduler = Schedule(d_model)
    optimizer = torch.optim.Adam(net.parameters(), lr=scheduler.next_step(step=1))

    train(net, encoder, optimizer, scheduler, args.gpu, args.rank, args.accumulate_steps)


def train(net, encoder,  optimizer, scheduler,device, rank, accumulate_steps): 
    z = open('logger', 'a')

    net.train()
    
    total_loss = 0.
    batches_done = 0
    p_size = 3840
    
    mem_steps = accumulate_steps
    

    for i in range(0,11):
        data = []
        
        with open(f'data/q{i}.txt', 'r') as f:
            for line in f:
                data.append(line.strip())
        
        print('steps_left:', ((11 - i) * len(data))/(mem_steps* args.batch_size))
        
        print(f'files number: {i}')

        for p in range(len(data)//p_size - 1):

            inputs, targets = get_samples(encoder, data[p*p_size:(p + 1)*p_size])
        
            dataset_train = CustomDataset(inputs, targets)
            train_sampler = torch.utils.data.distributed.DistributedSampler(dataset_train)
            train_loader = DataLoader(dataset_train, batch_size=args.batch_size, shuffle=(train_sampler is None), num_workers=0, 
                                        sampler=train_sampler)            
            step = 0

            
            for inputs, targets in train_loader:
                if  step == 0:
                    optimizer.zero_grad()

                inputs = inputs.cuda(device)
                targets = targets.cuda(device)

                size = inputs.size(1)
               
                input_mask = (inputs != 0).unsqueeze(1)
                nopeak_mask = np.triu(np.ones((1, size, size)), k=1)
                nopeak_mask = torch.autograd.Variable(torch.from_numpy(nopeak_mask) == 0).cuda(device)
                
                input_mask = input_mask & nopeak_mask
        
                outputs = net(inputs, input_mask)

                loss = F.cross_entropy(outputs.view(-1, outputs.size(-1)), targets.contiguous().view(-1),ignore_index=0)


                loss.mean().backward()                
                total_loss += loss.data                

                if step == (mem_steps - 1):
                    optimizer.step()
                    step = 0
                    batches_done  += 1 
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = scheduler.next_step(batches_done)

                    if batches_done % 200  == 0:
                        total_loss /= mem_steps
                        print(f'batch_idx: {(batches_done)} loss: {total_loss/200} time: {datetime.datetime.now().strftime("%H:%M:%S")} lr: {param_group["lr"]}')
                        z.write(f'batch_idx: {(batches_done)} loss: {total_loss/200} time: {datetime.datetime.now().strftime("%H:%M:%S")}\n')
                        total_loss = 0
                    if batches_done  % 2500 == 0:
                        if rank == 0:   
                            torch.save(net.state_dict(), f'checkpoints/checkpoint_batch_id_{batches_done}')

                else:
                    step += 1





if __name__=='__main__':
    main()