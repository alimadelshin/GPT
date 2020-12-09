import time
import unicodedata 
import os
import numpy as np
import re

path = 'place/2019-'

def unicode_to_ascii(s):
    return ''.join( c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')

def preprocess_sentence(w):
    w = unicode_to_ascii(w)

    w = re.sub(r"([?.!,])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)
    w = re.sub(r"[^a-zA-Z0-9?.!,]+", " ", w)
    w = w.rstrip().strip().lower()


    return w

miss_pairs = 0

lines = []
quests = []
replies = []

counter = 0
'''
f0 = open('unpqueries.txt', 'a', encoding = 'UTF-8')
f1 = open('unpreplies.txt', 'a', encoding = 'UTF-8')

for month in range(5, 13):
    with open(path + str(month) + '.txt', 'r', encoding = 'UTF-8', errors = 'ignore') as f:
        for line in f:
            if line == '<end examples>\n':
                if len(lines) > 1:
                    for r in range(len(lines) - 1):
                        quests.append(preprocess_sentence(lines[r]))
                        replies.append(preprocess_sentence(lines[r + 1]))
                    for r in range(len(quests)):
                        if len(quests[r].split()) + len(replies[r].split()) < 126:
                            f0.write(quests[r] + '\n')
                            f1.write(replies[r] + '\n')
                        else:
                            miss_pairs += 1
                    quests = []
                    replies = []
                    lines = []
                    counter += 1
                    if counter%100000 == 0:
                       print(counter)
            else:
                lines.append(line)

'''

f0 = open('pretraindata.txt', 'a')

for month in range(4, 13):
    with open(path + str(month) + '.txt', 'r', encoding= 'UTF-8', errors = 'ignore') as f:
        for line in f:
            if line != '<end examples>\n':
                line = preprocess_sentence(line)
                if len(line.split()) > 80 and len(line.split()) < 255:
                    f0.write(line + '\n')
                    counter += 1
                    if counter % 1000000 == 0:
                       print(counter)
                else:
                    miss_pairs += 1

print(counter)
print(miss_pairs)
                    






