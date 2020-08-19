#!/usr/bin/python3
import subprocess
import os


class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def cmd(commandline):
    with cd(project_dir):
        print(commandline)
        status, output = subprocess.getstatusoutput(commandline)
        # print(output)
        return status, output


def run(prog_path):
    with cd(project_dir):
        # print(prog_path)
        proc = subprocess.Popen(prog_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()  # stderr: summary, stdout:  each statement
        return stdout, stderr


project_dir = rootdir = "/home/lifter/BinRec/ncc_data/branch_emi/branch3_emi"
gcc_compile_cmd1 = "gcc -fno-stack-protector -no-pie -m32 -O0 -w -fpermissive {} -o {} -lm"
gcc_compile_cmd2 = "g++ -fno-stack-protector -no-pie -m32 -O0 -w -fpermissive {} -o {} -lm"
clang_path = '/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/clang-10 '
clang_compile_cmd1 = clang_path + " -fno-stack-protector -no-pie -O0 -w -fpermissive {} -o {} -lm"
clang_compile_cmd2 = clang_path + " -fno-stack-protector -no-pie -lstdc++ -O0 -w -fpermissive {} -o {} -lm"
clang_simple32_cmd = clang_path + " -O0 -m32 {} -o {}"
file_count = 0
for home, dirs, files in os.walk(rootdir):
    files.sort()
    for filename in files:
        if filename.endswith('.c'):
            # print(os.path.join(home, filename))
            out_file = filename[:-2] + ".out"
            project_dir = home
            if not os.path.exists(os.path.join(home, out_file)):
                print(os.path.join(home, filename))
                status, output = cmd(clang_simple32_cmd.format(filename, out_file))
                if status != 0:
                    # print("error\n", output)
                    status1, output1 = cmd(clang_compile_cmd2.format(filename+'c', out_file))
                    if status1 != 0:
                        # print(output)
                        if not ("fgets" in output1 or "was not declared in this scope" in output1):
                            print(output1)
                else:
                    file_count += 1
print("file_count,", file_count)
