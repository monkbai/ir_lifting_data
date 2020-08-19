#!/usr/bin/python3
import subprocess
import os
from prune_with_retdec import quick_prune

project_dir = "/home/lifter/ncc/data/result/mcsema_minus"


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


def clean(rootdir: str):
    global project_dir
    for home, dirs, files in os.walk(rootdir):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.out') :  # or filename.endswith('.cc') or filename.endswith('.txt'):
                print(os.path.join(home, filename))
                status, output = cmd("rm " + filename)


mcsema_cmd1 = "mcsema-disass --disassembler /home/lifter/idaedu-7.3/idat64 --os linux --arch amd64 --output {} --binary {} --entrypoint main --log_file {} "  # cfg, bin, log
mcsema_cmd2 = "mcsema-lift-4.0 --disable_optimizer true --arch amd64 --os linux --cfg {} --output {} "  # cfg, bc
llvm_dis = "/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-dis {} -o {}"  # bc, ll


def mcsema_all(rootdir: str):
    global project_dir
    failed_num = 0
    total_num = 0
    start_flag = False
    for home, dirs, files in os.walk(rootdir):
        project_dir = home
        files.sort()
        for filename in files:

            if home.endswith('/94') and filename == '4.out':
                start_flag = True
                continue

            if not start_flag:
                continue

            if filename.endswith('.out'):
                print(os.path.join(home, filename))
                total_num += 1
                cfg_file = filename[:-4] + '.cfg'
                bc_file = filename[:-4] + '.bc'
                log_file = filename[:-4] + '.log'
                ll_file = filename[:-4] + '.ll'
                if not os.path.exists(os.path.join(home, ll_file)):
                    status1, output1 = cmd(mcsema_cmd1.format(cfg_file, filename, log_file))
                    if status1 != 0:
                        continue
                    status2, output2 = cmd(mcsema_cmd2.format(cfg_file, bc_file))
                    if status2 != 0:
                        continue
                    status3, output3 = cmd(llvm_dis.format(bc_file, ll_file))

                    if os.path.exists(os.path.join(home, ll_file)):
                        cmd('rm ' + bc_file)
                        cmd('rm ' + cfg_file)
                        cmd('rm ' + log_file)
                    else:
                        failed_num += 1
                        print("error")
                # prune
                retdec_ll_file = filename + '.ll'
                dir_num = home.split('/')[-1]
                ll_path = os.path.join(home, ll_file)
                new_txt = quick_prune(dir_num, retdec_ll_file, ll_path)
                if new_txt == '':
                    cmd('rm ' + ll_file)
                else:
                    f = open(ll_path, 'w')
                    f.write(new_txt)
                    f.close()
    print('total_num:', total_num)
    print('failed_num:', failed_num)


if __name__ == '__main__':
    # mcsema_all("/home/lifter/ncc/data/result/clang_mcsema_minus")
    clean("/home/lifter/ncc/data/result/clang_mcsema_minus")
