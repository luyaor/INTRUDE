import sys
import main
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

result = main.get_TN(repo)
for x in result:
    print(x, file=f)

# end main program

if file:
    f.close()
