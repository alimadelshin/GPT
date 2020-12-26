import torch
import numpy as np
from torch.utils.data import Dataset


class CustomDataset(Dataset):

    def __init__(self, x, y):
        self.len = len(x)
        self.data_x = x
        self.data_y = y
    
    def __getitem__(self, index):
        return (self.data_x[index], self.data_y[index])
    
    def __len__(self):
        return self.len


def get_samples(encoder, samples):
    queries = []
    replies = []

    max_len = max([len(encoder.encode_as_ids(sample)) for sample in samples])

    for sample in samples:
        sample = encoder.encode_as_ids(sample) 
        inputs = sample[:-1] + [2] + [0]*(max_len - (len(sample)))
        outs = sample[1:] + [2] + [0]*(max_len - (len(sample)))

        queries.append(torch.tensor(inputs))
        replies.append(torch.tensor(outs))
    
    return queries, replies

