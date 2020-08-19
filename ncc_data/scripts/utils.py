#!/usr/bin/python3
import subprocess
import os

project_dir = '/home/lifter/ncc/data/result/ProgramData_32'


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


def check_x64(file_path):
    status, output = cmd('file '+file_path)
    if status == 0:
        if 'ELF 32-bit ' in output:
            return False
        elif 'ELF 64-bit ' in output:
            return True
    return False


def remove_x64():
    global project_dir
    remove_count = 0
    for home, dirs, files in os.walk("/home/lifter/ncc/data/result/ProgramData_32"):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.out'):
                print(os.path.join(home, filename))
                is_x64 = check_x64(os.path.join(home, filename))
                if is_x64:
                    cmd('rm ' + os.path.join(home, filename))
                    remove_count += 1
    print(remove_count, 'files are removed')


def compare():
    global project_dir
    lost_count = 0
    for home, dirs, files in os.walk("/home/lifter/ncc/data/result/clang_ir_x64"):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.ll'):
                print(os.path.join(home, filename))
                out_file = filename[:-3] + '.out'
                out_file_path = os.path.join(home, out_file)
                out_file_path = out_file_path.replace('clang_ir_x64', 'clang_mcsema')
                exist1 = os.path.exists(os.path.join(home, filename))
                exist2 = os.path.exists(out_file_path)
                if not exist1 or not exist2:
                    print("error")
                    lost_count += 1
    print(lost_count, ' out files are lost')


mcsema_cmd1 = "mcsema-disass --disassembler /home/lifter/idaedu-7.3/idat64 --os linux --arch amd64 --output {} --binary {} --entrypoint main --log_file {} "  # cfg, bin, log
mcsema_cmd2 = "mcsema-lift-4.0 --arch amd64 --os linux --cfg {} --output {} "  # cfg, bc
llvm_dis = "/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-dis {} -o {}"  # bc, ll
def mcsema_test(rootdir: str):
    global project_dir
    failed_num = 0
    total_num = 0
    for home, dirs, files in os.walk(rootdir):
        project_dir = home
        files.sort()
        for filename in files:
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

    print('total_num:', total_num)
    print('failed_num:', failed_num)


if __name__ == '__main__':
    # compare()
    # remove_x64()
    mcsema_test('/home/lifter/Documents/alias_test/branch_emi_mcsema')
    mcsema_test('/home/lifter/Documents/alias_test/fs_tests_mcsema')

    # mctoll_remove('/home/lifter/Documents/alias_test/branch_emi_mctoll')
    # mctoll_remove('/home/lifter/Documents/alias_test/fs_tests_mctoll')
