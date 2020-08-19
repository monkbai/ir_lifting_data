import os


base = "./spec_ir_mcsema_pruned/"
base = "./spec_ir_mcsema_minus_pruned/"
base = "./spec_ir_mcsema/"
base = "./spec_ir_mcsema_minus/"
base = "./spec_ir_retdec/"
base = "./spec_ir_clang_8/"
base = "./spec_ir_binrec/"

result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(base) for f in filenames if os.path.splitext(f)[1] == '.c']

def count(l):
    goto_count = 0
    while_count = 0
    for_count = 0
    switch_count = 0
    function_count = 0

    with open(l) as f:
        lines = f.readlines()
        for l in lines:
            if "goto " in l:
                goto_count += 1
            if l.endswith(") {\n") and ("while" in l or "for" in l or "if" in l or "switch" in l) == False:
                print l
                function_count += 1

    return (goto_count, function_count)


# ./spec_ir_clang_8/mcf/readmin.c
# spec_ir_clang_8/gobmk/engine/test.c
res = {}
for l in result:
    bn = l.split("/")[2]
    if "gcc" in bn or "perlbench" in bn:
        continue
    if bn not in res:
        (g, f) = count(l)
        res[bn] = [g, f]
    else:
        (g, f) = count(l)
        (g0, f0) = res[bn]
        res[bn] = (g + g0, f + f0)

print res
    
g = 0
f = 0
for k, v in res.items():
    g += v[0]
    f += v[1]

print (g / float(len(res)), f / float(len(res)))
