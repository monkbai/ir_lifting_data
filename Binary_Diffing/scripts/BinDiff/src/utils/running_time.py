from os import system
from subprocess import Popen, DEVNULL, PIPE

from src.utils.log import *


def run_cmd_with_time(cmd: list, time_file_path, log_on=False):
    time_cmd = ['/usr/bin/time', '-p']
    with open(time_file_path, 'w') as out:
        log(' '.join(cmd), LogType.RUN_CMD, _on=log_on)
        p = Popen(time_cmd + cmd, stdout=DEVNULL, stderr=out)
        return p


def run_cmd_with_time_subshell(cmd: str, time_file: str, log_on=False):
    test_cmd = '(time -p ' + cmd + ') 2> ' + time_file
    log(test_cmd, LogType.RUN_CMD, _on=log_on)
    return system(test_cmd)


def get_time_result(self, time_record):
    with open(time_record, 'r') as tr:
        lines = tr.readlines()
        for line in lines:
            if line.startswith('real '):
                time_str = line.split(' ')[-1]
                return float(time_str)
    return None


def run_cmd_with_perf_stat(cmd: list, stat_file_path, repeat=1, stdout_file_path=None, log_on=False):
    # need root to run
    perf_stat = ['/usr/bin/perf', 'stat', '-e', 'task-clock',
                 '--repeat', str(repeat), '-o', stat_file_path]
    #perf_stat = ['/usr/bin/chrt', '-f', '99', '/usr/bin/perf', 'stat',
    #             '-e', 'task-clock', '--repeat', str(repeat), '-o', stat_file_path]
    log(' '.join(cmd), LogType.RUN_CMD, _on=log_on)
    p = Popen(perf_stat + cmd, stdout=DEVNULL, stderr=PIPE)
    return p


def run_cmd_with_perf_stat_subshell(cmd: str, stat_file_path, stdout_file_path='/dev/null', log_on=False):
    test_cmd = 'sudo perf stat ' + cmd + ' > ' + stdout_file_path + ' 2> ' + stat_file_path
    log(test_cmd, LogType.RUN_CMD, _on=log_on)
    return system(test_cmd)


def get_perf_stat_result(stat_file_path: str):
    with open(stat_file_path, 'r') as sf:
        lines = sf.readlines()
        for line in lines:
            es = line.strip().split()
            if len(es) >= 2 and 'task-clock' in line:
                es[0] = es[0].replace(',', '')
                return float(es[0])
    raise Exception('cannot find task-clock value in file: %s' % stat_file_path)
    # for line in lines:
    #     if 'cycles' in line:
    #         es = line.split()
    #         cycles = float(es[0].replace(',', ''))
    #         cpu_frequency = float(es[3])
    #         return cycles, cpu_frequency
