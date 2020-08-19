#!/usr/bin/python3
import subprocess
import os
from threading import Timer
from subprocess import Popen, PIPE
import signal

project_dir = "/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang"


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


clang_compile_cmd1 = "clang-8 -fno-stack-protector -no-pie -O0 -w {} -o {} "
clang_compile_cmd2 = "clang-8 -fno-stack-protector -no-pie -m32 -O0 -w {} -o {} "


def compile_all():
    pass
new_txt = re.sub("void .*__remill[a-zA-Z0-9_]*\(.*\);\n", "", new_txt)
new_txt = re.sub("void .*__remill[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", new_txt)