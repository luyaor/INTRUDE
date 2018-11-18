import sys
import git

if len(sys.argv) > 1:
	infile = sys.argv[1].strip()
if len(sys.argv) > 2:
	outfile = sys.argv[2].strip()
else:
	outfile = infile + ".html"

with open(infile) as f:
	pairs = f.readlines()
with open(outfile, 'w') as f:
	pass

for ts in pairs:
	t = ts.split()

	r, n1, n2 = t[0], t[1], t[2]

	p1 = git.get_pull(r, n1)
	p2 = git.get_pull(r, n2)

	def get_state(p):
		if p["state"] == "open":
			return "open"
		if p1["merged_at"] is not None:
			return "merged"
		return "close"


	s1 = '[' + get_state(p1) + ']' + '<a href="https://github.com/%s/pull/%s" target="_blank"> %s </a>' % (r, n1, r + '/' + n1 + ':' + p1['title'])
	s2 = '[' + get_state(p2) + ']'  + '<a href="https://github.com/%s/pull/%s" target="_blank"> %s </a>' % (r, n2, r + '/' + n2 + ':' + p2['title'])

	with open(outfile, 'a', encoding="utf-8") as outf:
	    print(s1, '----', s2, '<hr>', file=outf)

