#!/usr/bin/python3
import subprocess
import os
import sys
import time

from src.utils.cmp_bins import get_bindiff_similarity


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


project_dir = rootdir = "./"

# DeepBinDiff_cmd = 'time python3 src/deepbindiff.py --input1 {} --input2 {} --outputDir {} > {}'

test_case_dir = '/export/d1/zliudc/revision_oakland2021/binary_analysis/BinDiff/ncc_test_clang/clang_O3/'

overall_time_consumption = 0.0


def compare_two(prog_1: str, prog_2: str, output_dir: str, log_path: str):
    global overall_time_consumption
    start_time = time.perf_counter()
    # status, output = cmd(DeepBinDiff_cmd.format(prog_1, prog_2, output_dir, log_path))
    # print(output)
    sim_score, conf_score = get_bindiff_similarity(prog_1, prog_2)
    with open(log_path, 'w') as f:
        f.write('{} * {}\n'.format(sim_score, conf_score))
        f.close()
    end_time = time.perf_counter()

    time_duration = end_time - start_time
    print('time duration: {}s'.format(time_duration)) 
    overall_time_consumption += time_duration


def get_overall_score(log_path: str):
    with open(log_path, 'r') as f:
        log_txt = f.read().strip('\n')
        score_list = log_txt.split('*')
        sim_score = float(score_list[0].strip())
        conf_score = float(score_list[1].strip())
        return sim_score, conf_score


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

        same_cat_score = 0
        not_same_cat_score = 0
        for idx in range(2):
            log_path = os.path.join(cur_dir, files[idx])
            
            #print('compare',)
            #print(prog_1, )
            #print(prog_2, )
            #print(log_path)
            sim_score, conf_score = get_overall_score(log_path)
            f_names = files[idx].split('_')
            if f_names[0].startswith(str(dir_num)+'-') and f_names[1].startswith(str(dir_num)+'-'):
                same_cat_score += sim_score * conf_score
            else:
                not_same_cat_score += sim_score * conf_score
            print(files[idx])
            print('sim_score {} * conf_score {}'.format(sim_score, conf_score))
            print(sim_score * conf_score)
        if same_cat_score > (not_same_cat_score + 0.00):
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
        bin1 = "/export/d1/zliudc/revision_oakland2021/binary_analysis/BinDiff/ncc_test/gcc_O0/1/1-1656.out"
        bin2 = "/export/d1/zliudc/revision_oakland2021/binary_analysis/BinDiff/ncc_test/gcc_O0/1/1-555.out"
        bin3 = "/export/d1/zliudc/revision_oakland2021/binary_analysis/BinDiff/ncc_test/gcc_O0/1/28-760.out"
        # sim_score, conf_score = get_bindiff_similarity(bin1, bin3)
        check_all_results()
