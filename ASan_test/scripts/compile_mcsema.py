#!/usr/bin/python3
import subprocess
import os
import sys
from threading import Timer

from pipes import quote
from pexpect import run


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


def popen_run(prog_path, asan=False):
    with cd(project_dir):
        # print(prog_path)
        if asan:
            proc = subprocess.Popen(prog_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()  # stderr: summary, stdout:  each statement
        else:
            proc = subprocess.Popen(prog_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()  # stderr: summary, stdout:  each statement
        return stdout, stderr


def input_run(cmd_str: str, asan=False, input_str='123\n123\n123\n'):
    with cd(project_dir):
        # print(prog_path)
        if asan:
            proc = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(input_str.encode('utf-8'))  # stderr: summary, stdout:  each statement
        else:
            proc = subprocess.Popen(cmd_str, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(input_str.encode('utf-8'))  # stderr: summary, stdout:  each statement

        if len(stdout) > 0:
            print('suspicious')
        return stdout, stderr


def timeout_run(cmd_str: str, asan=False, timeout_sec=1):
    with cd(project_dir):
        if asan:
            proc = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        timer = Timer(timeout_sec, proc.kill)
        try:
            timer.start()
            stdout, stderr = proc.communicate()
        finally:
            timer.cancel()
    return stdout, stderr


def pexpect_run(cmd_str: str, time_out=1):

    stdout, returncode = run("sh -c " + quote(cmd_str), withexitstatus=1, timeout=time_out)
    if returncode:
        signal = returncode - 128  # 128+n
    return stdout, ''


project_dir = rootdir = "../C/mcsema/testcases/"
# gcc_compile_cmd = "gcc -I /home/lifter/Documents/Juliet_Test/C/testcasesupport -DINCLUDEMAIN /home/lifter/Documents/Juliet_Test/C/testcasesupport/io.c {} -o {}"
# gpp_compile_cmd = "g++ -I /home/lifter/Documents/Juliet_Test/C/testcasesupport -DINCLUDEMAIN /home/lifter/Documents/Juliet_Test/C/testcasesupport/io.c {} -o {}"

mcsema_lift_cmd = 'mcsema-lift-4.0 --arch amd64 --os linux --cfg {} --output {} '
mcsema_recompile_cmd = 'remill-clang-4.0 -rdynamic -O3 -o {} {} /usr/local/lib/libmcsema_rt64-4.0.a -llzma -lm'

opt_asan_cmd = 'opt-4.0 --asan {} -o {}'  # input, output
mcsema_recompile_asan_cmd = 'remill-clang-4.0 -rdynamic -O3 -o {} {} /usr/local/lib/libmcsema_rt64-4.0.a -llzma -lm -lasan'  # output, input

llvm_dis = 'llvm-dis-4.0 {} -o {}'  # input, output
llvm_as = 'llvm-as-4.0 {} -o {}'  # input, output


def lift(the_dir: str):
    global project_dir
    file_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('.cfg'):
                # print(os.path.join(home, filename))
                bc_file = filename[:-4] + ".bc"
                if not os.path.exists(os.path.join(home, bc_file)):
                    # print(os.path.join(home, filename))
                    status, output = cmd(mcsema_lift_cmd.format(filename, bc_file))
                    if status != 0:
                        print(os.path.join(home, filename))
                        # print(output)
                    else:
                        file_count += 1
    print("file_count,", file_count)


def simple_recompile(the_dir: str):
    global project_dir
    file_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('.bc'):
                # print(os.path.join(home, filename))
                new_file = filename[:-3] + ".new"
                if not os.path.exists(os.path.join(home, new_file)):
                    # print(os.path.join(home, filename))
                    status, output = cmd(mcsema_recompile_cmd.format(new_file, filename))
                    if status != 0:
                        print(os.path.join(home, filename))
                        # print(output)
                    else:
                        file_count += 1
    print("file_count,", file_count)


def simple_check_results(the_dir: str):
    global project_dir
    failed_case_list = []
    same_count = 0
    not_same_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('.out'):
                # print(os.path.join(home, filename))
                new_file = filename[:-4] + ".new"
                if os.path.exists(os.path.join(home, new_file)):
                    print(os.path.join(home, filename))
                    same = compare(filename, new_file)
                    if not same:
                        print(os.path.join(home, filename))
                        failed_case_list.append(os.path.join(home, new_file))
                        # print(output)
                        not_same_count += 1
                    else:
                        same_count += 1
                    print('same {}, not same {}'.format(same_count, not_same_count))
    print("same_count,", same_count)
    print("not_same_count,", not_same_count)
    with open('./failed_case_list.log', 'w') as f:
        for case_name in failed_case_list:
            f.write(case_name + '\n')


def compare(prog_1: str, prog_2: str):
    prog_1 = os.path.join(project_dir, prog_1)
    prog_2 = os.path.join(project_dir, prog_2)
    stdout1, stderr1 = pexpect_run(prog_1)
    stdout2, stderr2 = pexpect_run(prog_2)
    if stdout1 == stdout2 and stderr1 == stderr2:
        return True
    return False


def add_asan(the_dir: str):
    global project_dir
    file_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('.bc') and not filename.endswith('_asan.bc'):
                # before apply the ASan instrumentation, modify the attribute #4 first
                modify_attribute(home, filename)

                # print(os.path.join(home, filename))
                new_bc_file = filename[:-3] + "_asan.bc"
                if not os.path.exists(os.path.join(home, new_bc_file)):
                    # print(os.path.join(home, filename))
                    status, output = cmd(opt_asan_cmd.format(filename, new_bc_file))
                    if status != 0:
                        print(os.path.join(home, filename))
                        # print(output)
                    else:
                        file_count += 1
    print("file_count,", file_count)


def recompile_asan(the_dir: str):
    global project_dir
    file_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('_asan.bc'):
                # print(os.path.join(home, filename))
                new_file = filename[:-3] + ".new"
                if not os.path.exists(os.path.join(home, new_file)):
                    # print(os.path.join(home, filename))
                    status, output = cmd(mcsema_recompile_asan_cmd.format(new_file, filename))
                    if status != 0:
                        print(os.path.join(home, filename))
                        # print(output)
                    else:
                        file_count += 1
    print("file_count,", file_count)


def check_results_asan(the_dir: str):
    global project_dir
    failed_cases_list = []
    with open('./failed_case_list.log', 'r') as f:
        txt = f.read()
        lines = txt.split('\n')
        for case_name in lines:
            failed_cases_list.append(case_name)
    file_count = 0
    asan_count = 0
    asan_positives_list = []
    asan_negatives_list = []
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('.out'):
                # print(os.path.join(home, filename))
                new_file = filename[:-4] + "_asan.new"
                if os.path.join(home, filename[:-4] + ".new") in failed_cases_list:
                    continue
                if os.path.exists(os.path.join(home, new_file)):
                    file_count += 1
                    print(os.path.join(home, filename))
                    has_asan, vul_type = check_asan(new_file)
                    if has_asan:
                        asan_count += 1
                        asan_positives_list.append(os.path.join(home, new_file)+'\n\t'+vul_type)
                    else:
                        asan_negatives_list.append(os.path.join(home, new_file)+'\n\t')
                    print('file_count {}, asan_count {}'.format(file_count, asan_count))
    print("asan_count,", asan_count)
    with open('./asan_positives_list.log', 'w') as f:
        for case_name in asan_positives_list:
            f.write(case_name + '\n')
    with open('./asan_negatives_list.log', 'w') as f:
        for case_name in asan_negatives_list:
            f.write(case_name + '\n')


def check_asan(prog_path, asan_flag=True):
    if 'get' in prog_path or 'scanf' in prog_path:
        stdout, stderr = input_run('LD_PRELOAD=libasan.so.4 ./' + prog_path, asan=asan_flag)
    elif 'socket' in prog_path:
        print('socket is difficult to handle')
        '''
        if 'listen_socket' in prog_path:
            stdout, stderr = run('LD_PRELOAD=libasan.so.4 ./' + prog_path)
            tmp1, tmp2 = run('python3 ./connect_socket.py')
        elif 'connect_socket' in prog_path:
            tmp1, tmp2 = run('python3 ./listen_socket.py')
            stdout, stderr = run('LD_PRELOAD=libasan.so.4 ./' + prog_path)
        '''
        return False, ''
    else:
        stdout, stderr = timeout_run('LD_PRELOAD=libasan.so.4 ./' + prog_path, asan=asan_flag)

    # stdout, stderr = timeout_run('LD_PRELOAD=libasan.so.4 ./' + prog_path)

    # stdout = stdout.decode('utf-8')
    # stderr = stderr.decode('utf-8')
    asan_bytes = 'ASAN'.encode('utf-8')
    as_bytes = 'AddressSanitizer'.encode('utf-8')
    segv_bytes = 'SEGV on unknown address'.encode('utf-8')
    good_bytes = '_good'.encode('utf-8')
    if asan_bytes in stdout or as_bytes in stdout:
        if segv_bytes in stdout:
            return False, ''
        else:
            return True, ''
    elif stderr and len(stderr) != 0 and (asan_bytes in stderr or as_bytes in stderr):
        if segv_bytes in stderr:
            return False, ''
        elif good_bytes in stderr:
            return False, ''
        else:
            vul_type = stderr.decode('utf-8').strip('\n').split('\n')[1]
            return True, vul_type
    return False, ''


def modify_attribute(home_dir: str, bc_file_path: str):
    def read_write(file_path='tmp.ll'):
        file_path = os.path.join(home_dir, file_path)
        with open(file_path, 'r') as f:
            ir_txt = f.read()
            ir_lines = ir_txt.split('\n')
            new_ir_txt = ''
            for line in ir_lines:
                if line.startswith('attributes #4 = { noinline nounwind'):
                    line = line.replace('noinline ', 'noinline sanitize_address ')
                new_ir_txt += line + '\n'
        with open(file_path, 'w') as f:
            f.write(new_ir_txt)

    global project_dir
    backup_dir = project_dir
    project_dir = home_dir

    # llvm-dis
    status, output = cmd(llvm_dis.format(bc_file_path, 'tmp.ll'))

    # modify the attribute #4
    read_write()

    # llvm-as
    status, output = cmd(llvm_as.format('tmp.ll', bc_file_path))

    # remove tmp file
    status, output = cmd('rm tmp.ll')

    project_dir = backup_dir


# deprecated
def delete_src(the_dir: str):
    global project_dir
    file_count = 0
    for home, dirs, files in os.walk(the_dir):
        files.sort()
        project_dir = home
        for filename in files:
            if filename.endswith('_asan.bc') or filename.endswith('_asan.new'):
                status, output = cmd("rm {}".format(filename))
                if status != 0:
                    print('error')
                file_count += 1
    print("file_count,", file_count)


if __name__ == '__main__':
    '''
    project_dir = './'
    test1 = '../testcases/CWE122_Heap_Based_Buffer_Overflow/s04/CWE122_Heap_Based_Buffer_Overflow__cpp_CWE806_char_memcpy_83.out'
    test2 = '../testcases/CWE122_Heap_Based_Buffer_Overflow/s04/CWE122_Heap_Based_Buffer_Overflow__cpp_CWE806_char_memcpy_83.new'
    compare(test1, test2)
    '''

    # project_dir = '/home/lifter/Documents/Juliet_Test/testcases/CWE122_Heap_Based_Buffer_Overflow/s11/'
    # check_asan('CWE122_Heap_Based_Buffer_Overflow__placement_new_12_asan.new')

    lift('/home/lifter/Documents/Juliet_Test/spec_binary/')
    # simple_recompile('/home/lifter/Documents/Juliet_Test/testcases/CWE124_Buffer_Underwrite')
    # simple_check_results('/home/lifter/Documents/Juliet_Test/testcases/')
    # add_asan('/home/lifter/Documents/Juliet_Test/testcases/')
    # recompile_asan('/home/lifter/Documents/Juliet_Test/testcases/')
    # check_results_asan('/home/lifter/Documents/Juliet_Test/testcases/')

    # delete_src("/home/lifter/Documents/Juliet_Test/testcases")
    if len(sys.argv) == 2:
        the_dir = sys.argv[1]
        print('start to process dir:', the_dir)
        lift(the_dir)
        # simple_recompile(the_dir)
        # add_asan(the_dir)
        # recompile_asan(the_dir)
        pass
