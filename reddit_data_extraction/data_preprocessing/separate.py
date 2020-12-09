count = 0

with open('data/pretrain.txt') as f:
    for line in f:
       count += 1

part = count//10
print(count)
i = 0
'''
queries = []
replies = []

with open('data/q.txt') as f:
    with open('data/r.txt') as g:
        for block in zip(f, g):

            if i%part == 0:
                z = open('force/q' + str(i//part) + '.txt', 'w')
                x = open('force/r' + str(i//part) + '.txt', 'w')

            z.write(block[0])
            x.write(block[1])

            i += 1
      '''      



with open('data/pretrain.txt', 'r') as f:
    for line in f:
        if i%part == 0:
            z = open('force/q' + str(i//part) + '.txt', 'w')
        z.write(line)
        i += 1

print(i)