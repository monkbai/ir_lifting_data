#!/usr/bin/python3
import subprocess
import os

rootdir = '/home/lifter/ncc/data/ProgramData/'
for home, dirs, files in os.walk(rootdir):
    for filename in files:
        print(os.path.join(home, filename))
        if filename.endswith('.txt'):
            c_file = filename[:-4]+".c"
            cc_file = filename[:-4] + ".cc"
            f = open(os.path.join(home, filename), "r", errors="ignore")
            cf = open(os.path.join(home, c_file), "w")
            ccf = open(os.path.join(home, cc_file), "w")
            cf.write("#include <stdio.h>\n#include <string.h>\n#include <math.h>\n\n")
            ccf.write("#include <cstdio>\n#include <cstring>\n#include <cmath>\n#include <iostream>\nusing namespace std;\n\n")
            code = f.read()

            code = code.replace("void main", "int main")
            code = code.replace("double main", "int main")
            code = code.replace("char main", "int main")

            cf.write(code)
            ccf.write(code)
            f.close()
            cf.close()
            ccf.close()
