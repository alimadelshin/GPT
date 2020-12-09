import pickle


def norm(path, path_, names, limit, delete = 1500):
    n_grams = dict()
    
    for name in names:
        gram = 3
        with open('gramms/' + str(gram) + name + '_' + '.pickle', 'rb') as handle:
            n_grams[str(gram) + name] = pickle.load(handle)
    
    pd = dict()
    
    for name in names:
        for i in range(1,3):
            with open('gramms/' + str(i) + name + '_' + '.pickle', 'rb') as handle:
                pd[str(i) + name] = pickle.load(handle)
    
    def reduction(tokens, name):

        if len(tokens) == 1:
            adr = str(1) + name
            token = tokens[0]
            if pd[adr].get(token):
                pd[adr][token] -= 1
                if pd[adr][token] < 800:
                    del pd[adr][token]
                return False
            else:
                return True
        
        elif len(tokens) == 2:
            adr = str(2) + name
            tokens = tuple(tokens)
            if pd[adr].get(tokens):
                pd[adr][tokens] -= 1
                if pd[adr][tokens] < 800:
                    del pd[adr][tokens]
                return False
            else:
                return True
            


    def cleanin(line, name):
        tokens = line.strip().replace('?', ' ').replace('!', ' ').replace('.', ' ').split()
        num = 3

        if len(tokens) == 0:
            return False
        
        if len(tokens) == 1 or len(tokens) == 2:
            return reduction(tokens, name)


        block = [0 for _ in tokens]
        n_grams_del = []
        
         
        if len(tokens) >= num: 
            temp_grams = zip(*[tokens[x:] for x in range(num)])
            for i, gram in enumerate(temp_grams):
                if n_grams[str(num) + name].get(gram):
                    block[i : i + num] = [1] * num
                    n_grams_del.append((str(num) + name, gram))
        
        if (1 - block.count(1)/len(block)) > limit:            
            for key0, key1 in n_grams_del:
                try:
                    if n_grams[key0][key1] < delete:
                        del n_grams[key0][key1]
    
                    else:
                        n_grams[key0][key1] -= 1
                except:
                    pass
            return True
        else:
            return False
        
    inp = open('u_queries.txt', 'w')
    tar = open('u_replies.txt', 'w')
    
    all_lines = 0
    skipped_lines = 0

    with open(path, 'r') as f:
        with open(path_, 'r') as g:
            for (i, (temp_inp, temp_tar)) in enumerate(zip(f, g)):
                if i % 10000000 == 0:
                    print(i)
                if cleanin(temp_inp, 'inp') and cleanin(temp_tar, 'tar'):
                    inp.write(temp_inp)
                    tar.write(temp_tar)

                else:
                    skipped_lines += 1
                
                all_lines = i
            
            print(limit, ' : ', skipped_lines/all_lines)



if __name__ == "__main__":
    for limit in [0.6]:
        norm('data/unpqueries.txt','data/unpreplies.txt', ['inp', 'tar'], limit)

                
 

         

