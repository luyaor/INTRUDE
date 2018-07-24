import sys
from main import *
if len(sys.argv) == 1:
    print('input repo name')
    repo = input().strip()
else:
    repo = sys.argv[1]
    file = None
    if len(sys.argv) > 2:
        file = sys.argv[2]
    
print('run', repo, 'output', file)

if file:
    f = open(file, 'w')
else:
    f = None

# main program
while True:
    try:
        run_and_save(repo)
        break
    except:
        print('error & restart!')
        pass
# end main program

if file:
    f.close()

