import pickle
from torchnlp.encoders.text import StaticTokenizerEncoder, pad_tensor, stack_and_pad_tensors


with open('data/tokens.pickle', 'rb') as f:
    temp_tokens = list(pickle.load(f).keys())
    
encoder = StaticTokenizerEncoder(temp_tokens, reserved_tokens=['<pad>', '<unk>', '</s>', '<s>', '<copy>', '<get_reply>'], tokenize= lambda s: s.split())

c = 0
d = 0

h = open('data/q.txt', 'w')
j = open('data/r.txt', 'w')

with open('data/queries.txt') as f:
    with open('data/replies.txt') as g:
        for query, reply in zip(f,g):
            string = encoder.encode(reply)
            count = [1 for word in string if word == 1]
            if (1 - len(count) / len(string)) > 0.9:
                h.write(query)
                j.write(reply)
                c += 1
            else:
                d += 1

            if c % 100000 == 0:
                print(c,d)