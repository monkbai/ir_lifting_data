#!/usr/bin/python3
import subprocess
import os
import sys
import time


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


project_dir = rootdir = "../DeepBinDiff/"

DeepBinDiff_cmd = 'time python3 src/deepbindiff.py --input1 {} --input2 {} --outputDir {} > {}'

test_case_dir = '/export/d1/zliudc/revision_oakland2021/binary_analysis/ncc_test/gcc_O0/'

overall_time_consumption = 0.0


def compare_two(prog_1: str, prog_2: str, output_dir: str, log_path: str):
    global overall_time_consumption
    start_time = time.perf_counter()
    status, output = cmd(DeepBinDiff_cmd.format(prog_1, prog_2, output_dir, log_path))
    print(output)
    end_time = time.perf_counter()

    time_duration = end_time - start_time
    print('time duration: {}s'.format(time_duration)) 
    overall_time_consumption += time_duration


def matched_pairs(log_path: str):
    with open(log_path, 'r') as f:
        log_txt = f.read()
        pairs_txt = log_txt[log_txt.find('matched pairs:'):]
        pairs_txt = pairs_txt[pairs_txt.find(':')+1:]
        pairs_count = pairs_txt.count('], [')
        return pairs_txt, pairs_count


def check_all_results():
    start_idx = 1
    end_idx = 104
    success_count = 0

    for dir_num in range(start_idx, end_idx+1):
        cur_dir = os.path.join(test_case_dir, str(dir_num))
        print(cur_dir)
        files = os.listdir(cur_dir)
        logfiles = filter(is_log, files)
        files = list(logfiles)
        files.sort()

        same_cat_count = 0
        not_same_cat_count = 0
        for idx in range(2):
            log_path = os.path.join(cur_dir, files[idx])
            
            #print('compare',)
            #print(prog_1, )
            #print(prog_2, )
            #print(log_path)
            pairs_txt, pairs_count = matched_pairs(log_path)
            f_names = files[idx].split('_')
            if f_names[0].startswith(str(dir_num)+'-') and f_names[1].startswith(str(dir_num)+'-'):
                same_cat_count += pairs_count
            else:
                not_same_cat_count += pairs_count
            print(files[idx])
            print(pairs_count)
        if same_cat_count > not_same_cat_count:
            print('success')
            success_count += 1
        else:
            print('failed')
            
    print('success count:', success_count)


def main(index):
    if index == 1:
        start_idx = 1
        end_idx = 26
    elif index == 2:
        start_idx = 27
        end_idx = 52
    elif index == 3:
        start_idx = 53
        end_idx = 78
    elif index == 4:
        start_idx = 79
        end_idx = 104
    
    compare_count = 0
    for dir_num in range(start_idx, end_idx+1):
        cur_dir = os.path.join(test_case_dir, str(dir_num))
        print(cur_dir)
        files = os.listdir(cur_dir)
        tmpfiles = filter(is_elf, files)
        files = list(tmpfiles)
        files.sort()

        for idx in range(2):
            prog_1 = os.path.join(cur_dir, files[idx])
            prog_2 = os.path.join(cur_dir, files[idx+1])
            output_dir = os.path.join(cur_dir, 'output'+files[idx][:-4]+'/')
            log_path = os.path.join(cur_dir, '{}_{}.log'.format(files[idx][:-4], files[idx+1][:-4]))
            
            #print('compare',)
            #print(prog_1, )
            #print(prog_2, )
            #print(log_path)
            compare_two(prog_1, prog_2, output_dir, log_path)
            compare_count += 1
    print('compare_count:', compare_count)
    print('overall_time_consumption:', overall_time_consumption)


def is_elf(x: str):
    return x.endswith('.out')


def is_log(x: str):
    return x.endswith('.log')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        test_case_dir = sys.argv[1]
        index = int(sys.argv[2])
        main(index)
    else:
        # test 
        # prog_1 = '/export/d1/zliudc/revision_oakland2021/binary_analysis/ncc_test/gcc_O0/1/1-1834.out'
        # prog_2 = '/export/d1/zliudc/revision_oakland2021/binary_analysis/ncc_test/gcc_O0/1/1-718.out'
        # output_dir = '/export/d1/zliudc/revision_oakland2021/binary_analysis/ncc_test/gcc_O0/1/output1-1834'
        # log_path = '/export/d1/zliudc/revision_oakland2021/binary_analysis/ncc_test/gcc_O0/1/same.log'
        # compare_two(prog_1, prog_2, output_dir, log_path)
        check_all_results()
        pass
