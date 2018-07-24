a = {}
with open('../data/msr_positive_pairs.txt') as f:
	for t in f.readlines():
		p, n1, n2 = t.split()
		if p not in a:
			a[p] = []
		a[p].append((n1,n2))


# z= ['angular/angular.js', 'mozilla-b2g/gaia', 'ceph/ceph', 'dotnet/corefx']
z = ['kubernetes/kubernetes','cocos2d/cocos2d-x','django/django','docker/docker']

for t in a:
	if t not in z:
		continue
	for o in a[t]:
		print(t, o[0], o[1])
 		
