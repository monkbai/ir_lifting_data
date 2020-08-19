# let's extract the following information from the svf context sensitive analysis outputs

# | MAYALIAS Accuracy | MUSTALIAS accuracy | NOALIAS accuracy | # of Pointers | # of Data Objects | # of CFG Node | # of CFG Edge |

import sys, os

# analyze bc for pointer alias information
# [FlowSensitive] Checking MAYALIAS
#         FAILURE :MAYALIAS check <id:47, id:45> at ({  })


def process(bc):
    alias_count = [0, 0, 0]
    alias_correct_count = [0, 0, 0]
    in_svfg = False
    to = 0
    te = 0
    tn = 0
    tp = 0
    os.system("wpa -fspta " + bc + " > log1.txt")
    
    with open("log1.txt") as f:
        lines = f.readlines()
        for l in lines:
            if "MAYALIAS check <" in l:
                if "FAILURE" in l:
                    alias_count[1] += 1
                elif "SUCCESS" in l:
                    alias_correct_count[1] += 1
                    alias_count[1] += 1
                else:
                    print("error " + l)
            elif "NOALIAS check <" in l:
                if "FAILURE" in l:
                    alias_count[0] += 1
                elif "SUCCESS" in l:
                    alias_correct_count[0] += 1
                    alias_count[0] += 1
                else:
                    print("error " + l)
            elif "MUSTALIAS check <" in l:
                if "FAILURE" in l:
                    alias_count[2] += 1
                elif "SUCCESS" in l:
                    alias_correct_count[2] += 1
                    alias_count[2] += 1
                else:
                    print("error " + l)
            elif l.startswith("TotalPointers"):
                # it's ok to have multiple "total pointers", we record the last one
                tp = int(l.split()[1])
            elif l.startswith("TotalObjects"):
                to = int(l.split()[1])
            elif "SVFG Statistics" in l:
                in_svfg = True
            elif in_svfg and l.startswith("TotalNode"):
                tn = int(l.split()[1])
            elif in_svfg and l.startswith("TotalEdge"):
                te = int(l.split()[1])
            elif in_svfg and "CallGraph Stats" in l:
                in_svfg = False
    
    assert (tp != 0 and tn != 0 and to != 0 and te != 0)
    
    return (alias_count, alias_correct_count, tp, to, tn, te)


must_alias_t = 0
may_alias_t = 0
no_alias_t = 0
must_alias_ct = 0
may_alias_ct = 0
no_alias_ct = 0
acc_t = 0
tp_t = 0
to_t = 0
tn_t = 0
te_t = 0
file_count = 0

def iterate_files(path):
    global must_alias_t
    global may_alias_t
    global no_alias_t
    global must_alias_ct
    global may_alias_ct
    global no_alias_ct
    global acc_t
    global tp_t
    global to_t
    global tn_t
    global te_t             
    global file_count
    
    for fn in os.listdir(path):
        if fn.endswith(".bc"):
            file_count += 1
            (ac, acc, tp, to, tn, te) = process(path + fn)
            print (ac, acc, tp, to, tn, te)
            no_alias_t += ac[0]
            may_alias_t += ac[1]
            must_alias_t += ac[2]
            no_alias_ct += acc[0]
            may_alias_ct += acc[1]
            must_alias_ct += acc[2]
            tp_t += tp
            to_t += to
            tn_t += tn
            te_t += te

def average():
    print (tp_t/float(file_count), to_t/float(file_count), tn_t/float(file_count), te_t/float(file_count))

    if (no_alias_ct != 0):
        print "no alias", no_alias_t / float(no_alias_ct)
    else:
        print "no alias", 1.0

    if (may_alias_ct != 0):
        print "may alias", may_alias_t / float(may_alias_ct)
    else:
        print "may alias", 1.0

    if (must_alias_ct != 0):
        print "must alias", must_alias_t / float(must_alias_ct)
    else:
        print "must alias", 1.0

    print "total analyzed alias fact", no_alias_ct + may_alias_ct + must_alias_ct


iterate_files("branch_emi/branch1_emi/")
iterate_files("branch_emi/branch2_emi/")
iterate_files("branch_emi/branch3_emi/")
iterate_files("fs_tests/")

average()

print "total file", file_count
