import re, sys, collections
run = sys.argv[1]
t = open(f'{run}/final/nl/accel_top.nl.v').read()
inst = re.findall(r'^\s*(sky130_\S+)\s+(\S+)\s*\((.*?)\);', t, re.S | re.M)
outs = {'X', 'Y', 'Q', 'Q_N', 'COUT', 'SUM', 'HI', 'LO', 'GCLK'}
drv, info = {}, {}
for cell, name, body in inst:
    pins = dict(re.findall(r'\.(\w+)\(\s*([^)]*?)\s*\)', body))
    info[name] = (cell, pins)
    for p, n in pins.items():
        if p in outs: drv[n] = name
bufpref = ('fanout', 'rebuffer', 'wire', 'split', 'load_slew', 'hold', 'input', 'max_cap', 'clone')

def parse(match):
    res, flag = [], False
    for l in open(f'{run}/55-openroad-stapostpnr/max_ss_100C_1v60/checks.rpt'):
        s = l.strip()
        if s.startswith('max ') and 'count' not in s:
            flag = match(s); continue
        if flag and 'VIOLATED' in l:
            res.append(l.split()[0])
    return res

for title, match in (('slew', lambda s: s == 'max slew'), ('cap', lambda s: s.startswith('max cap'))):
    roots = collections.Counter()
    for pin in parse(match):
        if '/' not in pin:
            roots['PORT ' + pin] += 1; continue
        i, p = pin.rsplit('/', 1)
        if i not in info or p not in info[i][1]: continue
        n = info[i][1][p]
        for _ in range(200):
            d = drv.get(n)
            if d is None:
                roots['PORT ' + n] += 1; break
            if not d.startswith(bufpref):
                roots[f"{n} (from {d}, {info[d][0]})"] += 1; break
            n = info[d][1]['A']
    print(f"\n== {title}")
    for r, c in roots.most_common(10):
        print(c, 'pins ->', r)
