import sys
from sklearn.utils import shuffle

def work(in_file, out_file, num):
    pairs = open(in_file).readlines()
    pairs = shuffle(pairs)[:num]
    with open(out_file, 'w') as out:
        for x in pairs:
            print(x.strip(), file=out)

if __name__ == "__main__":
    in_file = sys.argv[1].strip()
    out_file = sys.argv[2].strip()
    num = int(sys.argv[3].strip())
    work(in_file, out_file, num)
    
    