#!/usr/bin/python3
import subprocess
import os
from threading import Timer
from subprocess import Popen, PIPE
import signal


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


timeout_sec = 3
def run_with_timeout(cmd_line):
    global timeout_sec
    stdout = ''
    stderr = ''
    with cd(project_dir):
        proc = Popen(cmd_line, shell=True, stdout=PIPE, stderr=PIPE)
        timer = Timer(timeout_sec, proc.kill)
        try:
            timer.start()
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired as te:
            proc.kill()
            proc.terminate()
            # os.killpg(proc.pid, signal.SIGTERM)
            stderr = str(te)
        except Exception as e:
            stderr = str(e)
            pass
        finally:
            timer.cancel()
        return stdout, stderr


project_dir = ""
retdec_dir = "/home/lifter/ncc/data/result/clang_retdec"
mcsema_dir = "/home/lifter/ncc/data/mcsema/"
mcsema_cmd1 = "mcsema-dyninst-disass --os linux --arch amd64 --output {} --binary {} --entrypoint main "  # cfg, bin
mcsema_cmd2 = "mcsema-lift-4.0 --arch amd64 --os linux --cfg {} --output {} "  # cfg, bc
llvm_dis = "/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-dis {} -o {}"  # bc, ll
retdec_cmd = "/home/lifter/retdec/bin/retdec-decompiler.py {}"
file_count = 0


def rm_src(root_dir):
    global project_dir
    for home, dirs, files in os.walk(root_dir):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.c') or filename.endswith('.cc') or filename.endswith('.txt'):
                print(os.path.join(home, filename))
                status, output = cmd("rm "+filename)


def retdec_remove(root_dir):
    global project_dir
    start_flag = 0
    for home, dirs, files in os.walk(root_dir):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.bc') or filename.endswith('.c') or \
                    filename.endswith('.json') or filename.endswith('.dsm') or filename.endswith('.out'):
                print(os.path.join(home, filename))
                status, output = cmd("rm " + filename)


def mcsema_remove(root_dir):
    global project_dir
    start_flag = 0
    for home, dirs, files in os.walk(root_dir):
        project_dir = home
        files.sort()
        for filename in files:
            if filename.endswith('.out') or filename.endswith('.cfg') or filename.endswith('.bc'):
                print(os.path.join(home, filename))
                status, output = cmd("rm " + filename)


def retdec_lift(root_dir):
    global project_dir
    start_flag = 0
    for home, dirs, files in os.walk(root_dir):
        project_dir = home
        files.sort()
        for filename in files:
            if home.endswith('/18') and filename == '1678.out':
                start_flag = 1
                continue
            if start_flag == 0:
                continue
            if filename.endswith('.out'):
                print(os.path.join(home, filename))
                status, output = cmd(retdec_cmd.format(filename))
                # stdout, stderr = run_with_timeout(retdec_cmd.format(filename))  # too slow


def mcsema_lift(root_dir):
    global project_dir
    start_flag = 0
    for home, dirs, files in os.walk(root_dir):
        project_dir = home
        files.sort()
        for filename in files:
            if start_flag == 0 and home.endswith('/89'):
                start_flag = 1
                continue
            if start_flag == 0:
                continue
            if filename.endswith('.out'):
                print(os.path.join(home, filename))
                cfg_file = filename[:-4] + '.cfg'
                bc_file = filename[:-4] + '.bc'
                ll_file = filename[:-4] + '.ll'
                status, output = cmd(mcsema_cmd1.format(cfg_file, filename))
                if status != 0:
                    continue
                status, output = cmd(mcsema_cmd2.format(cfg_file, bc_file))
                if status != 0:
                    continue
                status, output = cmd(llvm_dis.format(bc_file, ll_file))

                if os.path.exists(os.path.join(home, ll_file)):
                    cmd('rm ' + bc_file)
                    cmd('rm ' + cfg_file)
                    pass
                else:
                    print("error")


# rm_src(retdec_dir)
# rm_src(mcsema_dir)
retdec_lift(retdec_dir)
retdec_remove(retdec_dir)
# mcsema_lift(mcsema_dir)
# mcsema_remove(mcsema_dir)

