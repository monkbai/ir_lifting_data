#!/usr/bin/python3
import subprocess
import os
import sys


# ---------------------------------------
# Utils
# ---------------------------------------

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


project_dir = rootdir = "../C/testcases/"


def remove_no_pie(file_path: str):
    with open(file_path, 'r') as f:
        txt = f.read()
        txt = txt.replace('-no-pie', '-fPIE')
        f.close()
    with open(file_path, 'w') as f:
        f.write(txt)
        f.close()


def modify_makefiles():
    global project_dir
    for home, dirs, files in os.walk(rootdir):
        files.sort()
        project_dir = home
        for f in files:
            if f.startswith('Makefile') and not f.endswith('.backup'):
                file_path = os.path.join(home, f)
                print(file_path)
                # status, output = cmd('cp {} {} '.format(f, f+'.backup'))
                remove_no_pie(file_path)


if __name__ == '__main__':
    modify_makefiles()
