#!/usr/bin/python3
import subprocess
import os
import sys
from time import time

# project_dir = '/home/lifter/BinRec'
project_dir = pathV = os.environ["S2EDIR"]


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


def debug(break_point: str):
    # input(break_point)
    print('')


backup_file = os.path.join(project_dir, 'plugins/config.debian.lua.backup')
print("backup_file:", backup_file)
config_lua = os.path.join(project_dir, 'plugins/config.debian.lua')
print("config_lua:", config_lua)
def set_base_dirs(add_dir: str):
    f = open(backup_file, 'r')
    config_txt = f.read()
    f.close()

    config_txt = config_txt.replace('<REPLACE_TARGET_OF_BASE_DIRS>', add_dir)

    f = open(config_lua, 'w')
    f.write(config_txt)
    f.close()


def handle_failed_case(dir_str: str, file_str: str):
    global project_dir
    project_dir = dir_str
    status, output = cmd("mkdir skip")

    file_list = os.listdir(dir_str)
    file_list.sort()
    
    for file in file_list:
        if not os.path.isdir(os.path.join(dir_str, file)) or file == "merged" or file == "skip" or file == "0":
            continue
        succs_dat = os.path.join(dir_str, file)
        succs_dat = os.path.join(succs_dat, "succs.dat")
        if not os.path.exists(succs_dat):
            project_dir = dir_str
            print("skip", file, ": without succs.dat")
            status, output = cmd('mv ./' + file + ' ./skip/'+file)
    
    for file in file_list:
        # print("debug ", os.path.join(dir_str, file), "is dir ", os.path.isdir(os.path.join(dir_str, file)))
        if not os.path.isdir(os.path.join(dir_str, file)) or file == "merged" or file == "skip" or file == "0":
            continue
        print("try to skip trace", file)

        # try to skip one of these trace
        project_dir = dir_str
        status, output = cmd("rm -rf ./merged")
        status, output = cmd('mv ./' + file + ' ./skip/'+file)

        # merge rest of these traces
        project_dir = os.environ["S2EDIR"]
        status, output = cmd('./scripts/merge_traces.sh ' + file_str + '-1')  # generate merged dir

        # lift
        project_dir = dir_str + "/merged"
        status, output = cmd('../../scripts/lift.sh captured.bc lifted.bc')
        if status == 0:
            debug('lift success')
            return 0
        # print(output)
        debug('lift failed')
    print(output)
    return -1



def lift_all_file(rootdir: str, sym_in: str):
    global project_dir
    file_list = os.listdir(rootdir)
    file_list.sort()
    total_time = 0
    for f in file_list:
        f_path = os.path.join(rootdir, f)

        if os.path.isfile(f_path) and f_path.endswith('.out'):
            project_dir = os.environ["S2EDIR"]
            root_bc_path = f_path[:-4] + '.bc'
            root_ll_path = f_path[:-4] + '.ll'

            if os.path.exists(root_bc_path) and os.path.exists(root_ll_path):
                continue
            if os.path.exists(os.path.join(project_dir, "s2e-out-" + f + "-1")):
                # merge traces
                # print('\n--------\n--- merge trace \n--------')
                # status, output = cmd('./scripts/double_merge.sh ' + f)
                # debug('-- input any key to continue ')
                print('\n--------\n--- merge trace \n--------')
                status, output = cmd('./scripts/merge_traces.sh ' + f + '-1')
                debug('-- input any key to continue ')

                # lift
                print('\n--------\n--- lift \n--------')
                result_dir = 's2e-out-' + f + '-1/merged'
                project_dir = os.path.join(project_dir, result_dir)
                status, output = cmd('../../scripts/lift.sh captured.bc lifted.bc')
                if status != 0:
                    # print(output)
                    debug('before handle_failed_cases ')
                    status = handle_failed_case(os.path.dirname(project_dir), f)
                    if status != 0:
                        print("ERROR: still failed\n")
                debug('-- input any key to continue ')

                # lower
                print('\n--------\n--- lower \n--------')
                project_dir = os.environ["S2EDIR"] + '/s2e-out-' + f + '-1/merged'
                status, output = cmd('../../scripts/lower.sh lifted.bc recovered.bc')
                debug('-- input any key to continue ')

                # move .ll and .bc file to rootdir
                print('\n--------\n--- move to root dir \n--------')
                result_bc_file = 'recovered.bc'
                result_ll_file = 'recovered.ll'
                bc_path = os.path.join(project_dir, result_bc_file)
                ll_path = os.path.join(project_dir, result_ll_file)
                if os.path.exists(bc_path) and os.path.exists(ll_path):
                    status, output = cmd('cp ' + bc_path + ' ' + root_bc_path)
                    status, output = cmd('cp ' + ll_path + ' ' + root_ll_path)
                else:
                    print('.bc or .ll file not found')
                debug('-- input any key to continue ')
                continue

            start_time = time()
            print('\n--------\n--- start lifting :', f_path,'\n--------')

            # set base dirs in plugins/config.debian.lua
            print('\n--------\n--- set base dirs in config.debian.lua \n--------')
            set_base_dirs(rootdir)
            debug('-- input any key to continue ')

            # run symbolic execution - timeout: 600 s
            print('\n--------\n--- run symbolic execution \n--------')
            status, output = cmd('./qemu/cmd-debian.sh --vnc 0 ' + sym_in + f)  # TODO add symbolic input at here
            print('status', status, 'output', 'skip')
            debug('-- input any key to continue ')

            """
            # clean
            # print('\n--------\n--- clean \n--------')
            # project_dir = '/home/lifter/BinRec'
            # status, output = cmd('rm -rf ./s2e-out-*')
            # status, output = cmd('rm ./s2e-last')
            # debug('-- input any key to continue ')
            """

            print('\n--------\n--- elapsed time \n--------')
            end_time = time()
            elapsed = end_time - start_time
            print(str(elapsed) + 's passed', )
            f = open('./time.log', 'a')
            f.write(f_path + '\n')
            f.write(str(elapsed) + '\n')
            f.close()
            total_time += elapsed
            debug('-- input any key to continue ')
    print('TOTAL TIME:', str(total_time))
    return total_time


if __name__ == '__main__':
    container_id = sys.argv[1]
    container_id = int(container_id)
    print("CONTAINER ID:", container_id)
    tot_time = 0
    if container_id == 1:
        # container 1
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/1', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/2', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/3', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/4', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/5', ' --sym-stdin 12 ')
    elif container_id == 2:
        # container 2
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/6', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/7', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/8', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/9', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/10', ' --sym-stdin 12 ')
    elif container_id == 3:
        # container 3
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/11', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/12', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/13', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/14', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/15', ' --sym-stdin 12 ')
    elif container_id == 4:
        # container 4
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/16', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/17', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/18', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/19', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/20', ' --sym-stdin 12 ')
    elif container_id == 5:
        # container 5
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/21', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/22', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/23', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/24', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/25', ' --sym-stdin 4 ')
    elif container_id == 6:
        # container 6
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/26', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/27', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/28', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/29', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/30', ' --sym-stdin 4 ')
    elif container_id == 7:
        # container 7
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/31', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/32', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/33', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/34', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/35', ' --sym-stdin 12 ')
    elif container_id == 8:
        # container 8
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/36', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/37', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/38', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/39', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/40', ' --sym-stdin 20 ')
    elif container_id == 9:
        # container 9
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/41', '')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/42', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/43', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/44', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/45', ' --sym-stdin 8 ')
    elif container_id == 10:
        # container 10
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/46', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/47', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/48', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/49', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/50', ' --sym-stdin 4 ')
    elif container_id == 11:
        # container 11
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/51', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/52', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/53', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/54', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/55', ' --sym-stdin 8 ')
    elif container_id == 12:
        # container 12
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/56', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/57', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/58', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/59', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/60', ' --sym-stdin 4 ')
    elif container_id == 13:
        # container 13
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/61', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/62', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/63', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/64', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/65', ' --sym-stdin 12 ')
    elif container_id == 14:
        # container 14
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/66', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/67', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/68', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/69', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/70', ' --sym-stdin 12 ')
    elif container_id == 15:
        # container 15
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/71', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/72', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/73', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/74', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/75', ' --sym-stdin 20 ')
    elif container_id == 16:
        # container 16
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/76', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/77', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/78', '')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/79', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/80', ' --sym-stdin 12 ')
    elif container_id == 17:
        # container 17
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/81', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/82', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/83', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/84', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/85', ' --sym-stdin 4 ')
    elif container_id == 18:
        # container 18
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/86', ' --sym-stdin 20 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/87', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/88', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/89', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/90', ' --sym-stdin 12 ')
    elif container_id == 19:
        # container 19
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/91', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/92', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/93', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/94', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/95', ' --sym-stdin 8 ')
    elif container_id == 20:
        # container 20
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/96', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/97', ' --sym-stdin 4 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/98', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/99', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/100', ' --sym-stdin 12 ')
    elif container_id == 21:
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/101', '')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/102', ' --sym-stdin 12 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/103', ' --sym-stdin 8 ')
        tot_time += lift_all_file('/home/xxxxx/BinRec/ncc_data/poj_binrec/104', ' --sym-stdin 8 ')
    print('total_time:', tot_time)
