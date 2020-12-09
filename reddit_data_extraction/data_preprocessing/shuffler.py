import os
import random

i = 0

with open('data/pretraindatareal.txt', 'r') as f:
    while f.readline():
        i += 1

part = i//14 - 1

print(f'size: {i}, part_size: {part}')
'''
with open('data/q.txt', 'r') as f:
    with open('data/r.txt', 'r') as g:
        k = open('q.txt', 'w')
        l = open('r.txt', 'w')

        shuffle_block = []

        for i, block in enumerate(zip(f, g)):
            shuffle_block.append(block)
            
            if i % part == 0:
                print(len(shuffle_block))
                random.shuffle(shuffle_block)
                for q, r in shuffle_block:
                    k.write(q)
                    l.write(r)
                
                shuffle_block = []
        


                   

        '''


with open('data/pretraindatareal.txt', 'r') as f:
    k = open('pretr.txt', 'w')
    shuffle_block = []

    for i, block in enumerate(f):
        shuffle_block.append(block)
            
        if (i + 1) % part == 0:
            print(len(shuffle_block))
            random.shuffle(shuffle_block)
            for q in shuffle_block:
                k.write(q)

            shuffle_block = []
         


                   

