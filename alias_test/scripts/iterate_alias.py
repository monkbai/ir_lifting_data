import os

alias_opt = ["-aa", "-aa-eval", "-amdgpu-aa", "-basicaa", "-cfl-anders-aa", "-cfl-steens-aa", "-external-aa", "-globals-aa", "-objc-arc-aa", "-scev-aa", "-scoped-noalias", "-tbaa", "-scoped-noalias"]


# 28 Total Alias Queries Performed
# 22 no alias responses (78.5%)
# 0 may alias responses (0.0%)
# 2 partial alias responses (7.1%)
# 4 must alias responses (14.2%)

def parse_output():
    res = []
    with open("log") as f:
        lines = f.readlines()
        for l in lines:
            if "no alias response" in l:
                res.append(int(l.split()[0]))
            elif "may alias response" in l:
                res.append(int(l.split()[0]))
            elif "partial alias response" in l:
                res.append(int(l.split()[0]))
            elif "must alias response" in l:
                res.append(int(l.split()[0]))
    return res


for o in alias_opt:
    # opt -aa  -aa-eval -print-alias-sets -disable-output t.bc
    cmd = "opt-10 " + o + " -aa-eval -print-alias-sets -disable-output t2.bc"
    os.system(cmd + " 2> log")
    print o, parse_output()


