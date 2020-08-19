#!/usr/bin/python3
import subprocess
import os
from threading import Timer
from subprocess import Popen, PIPE
import signal

project_dir = "/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_mcsema_minus"


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


mcsema_cmd1 = "mcsema-disass --disassembler /home/lifter/idaedu-7.3/idat64 --os linux --arch amd64 --output {} --binary {} --entrypoint main --log_file {} "  # cfg, bin, log
mcsema_cmd2 = "mcsema-lift-4.0 --disable_optimizer true --arch amd64 --os linux --cfg {} --output {} "  # cfg, bc


def mcsema_all():
    global project_dir
    failed_num = 0
    total_num = 0
    start_flag = True
    for home, dirs, files in os.walk("/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_mcsema_minus"):
        project_dir = home
        files.sort()
        for filename in files:

            #if home.endswith('/44') and filename == '1278.out':
            #    start_flag = True
            #    continue

            if not start_flag:
                continue

            if filename.endswith('.out'):
                cfg_name = filename[:-4]+'.cfg'
                log_name = filename[:-4]+'.log'
                bc_name = filename[:-4]+'.bc'
                
                print(os.path.join(home, filename))
                total_num += 1
                status, output = cmd(mcsema_cmd1.format(cfg_name, filename, log_name))
                if status != 0:
                    failed_num += 1
                    print('error, debug')
                status, output = cmd(mcsema_cmd2.format(cfg_name, bc_name))    
    print('total_num:', total_num)
    print('failed_num:', failed_num)


if __name__ == '__main__':
    mcsema_all()
    # clean()

