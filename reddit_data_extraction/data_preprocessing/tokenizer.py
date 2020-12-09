import pickle

tokens_d = dict()
buffer = 5000000
rows = 0

def clean(tokens_d, size):
    temp = dict()
    
    values = list(tokens_d.values())
    values.sort(reverse=True)
    values = values[:size]
    for key, val in tokens_d.items():
        if val in values:
            temp[key] = val
            del values[values.index(val)]
            if not values:
                break
    
    return temp


with open('data/replies.txt', 'r') as f:
    for line in f:
        tokens = line.lower().rstrip().replace('.', ' ').replace('?', ' ').replace('!', ' ').replace(',', ' ').split()
        rows += 1
        for token in tokens:
            if tokens_d.get(token):
                tokens_d[token] += 1
            else:
                tokens_d[token] = 1
        
        if rows % buffer == 0:
            print(rows)
            tokens_d = clean(tokens_d, 50000)

    with open('tokens.pickle', 'wb') as handle:
        pickle.dump(clean(tokens_d, 25000), handle)





