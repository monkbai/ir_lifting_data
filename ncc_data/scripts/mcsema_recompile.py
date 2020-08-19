#!/usr/bin/python3
import subprocess
import os
from prune_with_retdec import quick_prune

project_dir = "./"


check_program_list = ['1/1002.out',
'2/1002.out',
'3/1001.out',
'4/1007.out',
'7/1.out',
'8/1.out',
'9/1.out',
'10/1.out',
'11/1.out',
'14/145.out',
'16/1.out',
'18/1.out',
'19/1.out',
'20/1.out',
'21/1.out',
'22/1002.out',
'23/1001.out',
'24/1.out',
'26/1.out',
'27/104.out',
'28/11.out',
'29/1.out',
'30/91.out',
'31/139.out',
'32/11.out',
'33/11.out',
'34/122.out',
'35/1.out',
'36/1001.out',
'37/1001.out',
'38/1002.out',
'40/1644.out',
'43/1.out',
'44/1.out',
'46/1012.out',
'47/70.out',
'48/2.out',
'49/1.out',
'50/13.out',
'51/10.out',
'52/2029.out',
'53/1.out',
'54/1002.out',
'55/102.out',
'56/1004.out',
'57/11.out',
'58/10.out',
'59/1.out',
'60/1.out',
'61/1.out',
'62/1.out',
'65/1.out',
'66/10.out',
'68/10.out',
'69/1.out',
'70/101.out',
'71/1001.out',
'72/1.out',
'73/104.out',
'74/1001.out',
'76/1.out',
'77/1.out',
'78/1.out',
'79/1004.out',
'80/11.out',
'81/1.out',
'82/1.out',
'83/1.out',
'84/1.out',
'85/1.out',
'86/1001.out',
'87/100.out',
'88/11.out',
'89/101.out',
'90/1.out',
'93/1000.out',
'94/1004.out',
'95/1.out',
'96/1.out',
'97/102.out',
'98/102.out',
'99/1001.out',
'100/103.out',
'102/1.out',
'103/1.out',
'104/100.out']


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


def copy_programs():
    from_dir = '/home/lifter/ncc/data/result/ProgramData_clang'
    to_dir = '/home/lifter/ncc/data/result/mcsema_recompile'
    for dir_num in range(1, 105):
        dir_path = os.path.join(to_dir, str(dir_num))
        print(dir_path)
        status, output = cmd('mkdir ' + dir_path)
    for prog in check_program_list:
        from_file = os.path.join(from_dir, prog)
        to_file = os.path.join(to_dir, prog)
        status, output = cmd('cp ' + from_file + ' ' + to_file)


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
mcsema_cmd2 = "mcsema-lift-4.0 --arch amd64 --os linux --cfg {} --output {} "  # cfg, bc
llvm_dis = "/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-dis {} -o {}"  # bc, ll
mcsema_recompile = "remill-clang-4.0 -rdynamic -O3 -o {} {} /usr/local/lib/libmcsema_rt64-4.0.a -llzma -lm" # .new, .bc


def mcsema_all():
    global project_dir

    project_dir = target_dir = '/home/lifter/ncc/data/result/mcsema_recompile'
    for prog in check_program_list:
        filename = os.path.join(target_dir, prog)
        cfg_file = filename[:-4] + '.cfg'
        log_file = filename[:-4] + '.log'
        bc_file = filename[:-4] + '.bc'

        current_dir = os.path.dirname(filename)
        project_dir = current_dir

        status1, output1 = cmd(mcsema_cmd1.format(cfg_file, filename, log_file))
        status2, output2 = cmd(mcsema_cmd2.format(cfg_file, bc_file))


def recompile_all():
    global project_dir

    project_dir = target_dir = '/home/lifter/ncc/data/result/mcsema_recompile'
    for prog in check_program_list:
        filename = os.path.join(target_dir, prog)
        bc_file = filename[:-4] + '.bc'
        new_file = filename[:-4] + '.new'

        current_dir = os.path.dirname(filename)
        project_dir = current_dir

        status, output = cmd(mcsema_recompile.format(new_file, bc_file))
        if status != 0:
            print(output)


if __name__ == '__main__':
    # copy_programs()
    # mcsema_all()
    recompile_all()
