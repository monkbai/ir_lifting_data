import commands, os, subprocess

test_cases = {}


#base = "ProgramData/"
base = "clang_retdec/"
#base = "mcsema_gcc_no_trim/"
#base = "mctoll_gcc/"

def prepare_test_cases():
    global test_cases
    with open("check_input_output.txt") as f:
        lines = f.readlines()
        for l in lines:
            print l
            if (l.strip() == ""):
                continue
            else:
                if "skip" in l:
                    continue
                else:
                    if l.startswith("9:"):
                        # quick hack
                        test_cases["9"] = ('4 "a" 33 "b" 55 "d" 28 "c" 1', ''.join('a b d c'.split()))
                    elif l.startswith("99:"):
                        # quick hack
                        test_cases["99"] = ('2 12 13', ''.join('1-18: 100.00% 19-35: 0.00% 36-60: 0.00% 60??: 0.00%'.split()))
                    else:
                        c = l.split(":")[0]
                        t = l.split(":")[1]
                        i = '"' + t.split('"')[1] + '"'
                        o = t.split('"')[2]
                        test_cases[c] = (i, "".join(o.split()))

def compile(p):
    # retdec xx.out.ll
    #p1 = p[:-2] + "out-dis.ll"
    p1 = p[:-2] + "out.ll"
    c_p = ("clang-10 -lm -O0 " +  base + p1)
    print c_p
    os.system(c_p)

from subprocess import check_output

def run(l):
    l1 = "/".join(l.split("/")[:-1])
    c_p = l1 +  "/a.out "
    c = l.split("/")[0]
    print test_cases[c]
    (i, o) = test_cases[c]
    # cmd = base + c_p
    cmd = "./a.out"
    cmd0 = 'echo ' + i
    p1 = subprocess.Popen(cmd0, shell=True, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd, shell=True, stdin=p1.stdout, stdout=subprocess.PIPE)
    o1,e = p2.communicate()
    print o1
    if (o == "".join(o1.split())):
        return True
    else:
        return False

prepare_test_cases()
lines = []
t_c = 0
t = 0
with open("check_program_list.txt") as f:
    lines = f.readlines()
    for l in lines:
        os.system("rm a.out")
        t_c += 1
        compile(l)
        if run(l):
            t += 1
        # break
        #print commands.getstatusoutput('wc -l file')
print t / float(t_c), t, t_c
