#!/usr/bin/python3
import subprocess
import os
from threading import Timer
from subprocess import Popen, PIPE
import signal

project_dir = "/home/lifter/ncc/data/result/mctoll"


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


def clean():
    global project_dir
    for home, dirs, files in os.walk("/home/lifter/ncc/data/result/clang_mctoll"):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.c') or filename.endswith('.cc') or filename.endswith('.txt') or filename.endswith('.out'):
                print(os.path.join(home, filename))
                status, output = cmd("rm " + filename)


mctoll_cmd = '/home/lifter/llvm-project/build/bin/llvm-mctoll -d {}'


def mctoll_all():
    global project_dir
    failed_num = 0
    total_num = 0
    start_flag = False
    for home, dirs, files in os.walk("/home/lifter/ncc/data/result/clang_mctoll"):
        project_dir = home
        files.sort()
        for filename in files:

            if home.endswith('/44') and filename == '1278.out':
                start_flag = True
                continue

            if not start_flag:
                continue

            if filename.endswith('.out'):
                ll_name = filename+'-dis.ll'
                if ll_name in files:
                    continue
                print(os.path.join(home, filename))
                total_num += 1
                status, output = cmd(mctoll_cmd.format(filename))
                if status != 0:
                    failed_num += 1
                    # print('error, debug')
                    if 'Unsupported undefined function' in output:
                        output = output[:output.find('undefined function')+18]
                        print(output)
                        f = open('./tmp1.txt', 'a+')
                        f.write(output+'\n')
                        f.close()
    print('total_num:', total_num)
    print('failed_num:', failed_num)


if __name__ == '__main__':
    # mctoll_all()
    clean()
