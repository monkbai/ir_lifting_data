import os
import re
import subprocess


class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

project_dir = '/home/lifter/ncc/data/result/mcsema'
def cmd(commandline):
    with cd(project_dir):
        print(commandline)
        status, output = subprocess.getstatusoutput(commandline)
        # print(output)
        return status, output


# define %struct.Memory* @sub_400557_main(%struct.State* noalias dereferenceable(3376) %0, i64 %1, %struct.Memory* noalias %2) local_unnamed_addr #4 !remill.function.type !1244 !remill.function.tie !1274 {
reg_str = r"define .* (@[a-zA-Z0-9_]+)\((.*)\).*{"
def func_name(line):
    match_obj = re.match(reg_str, line)
    if not match_obj:
        return ''
    f_name = match_obj.group(1)
    para = match_obj.group(2)
    return f_name


def black_list(func_name: str):
    if func_name == '':
        return False
    elif func_name.startswith('@ext'):
        return False
    elif '_ZN12_GLOBAL_' in func_name:  # dangerous
        return False

    if func_name.endswith('__fini'):
        return True
    elif func_name.endswith('__init'):
        return True
    elif func_name.endswith('___libc_csu_fini'):
        return True
    elif func_name.endswith('___libc_csu_init'):
        return True
    elif func_name.endswith('wrapper'):
        return True
    elif func_name.endswith('frame_dummy'):
        return True
    elif func_name.endswith('__start'):
        return True
    elif func_name.endswith('do_global_dtors_aux'):
        return True
    elif func_name.endswith('register_tm_clones'):
        return True
    elif func_name.endswith('relocate_static_pie'):
        return True
    elif 'mcsema' in func_name:
        return True
    elif 'initialization' in func_name:  # dangerous
        return True
    elif 'destruction' in func_name:  # dangerous
        return True
    elif 'GLOBAL' in func_name:  # dangerous
        return True
    # elif 'gnu_cxx11' in func_name:
    #     return True
    elif not re.match('@sub_[0-9]+', func_name):
        return True

    return False


def prune(IR_file):
    removed_funcs = []

    f = open(IR_file, 'r')
    IR_txt = f.read()
    IR_lines = IR_txt.split('\n')
    func_count = 0
    mark_lines = [1 for i in range(len(IR_lines))]
    in_func_flag = 1
    for i in range(len(IR_lines)):
        line = IR_lines[i]
        f_name = func_name(line)
        in_black = black_list(f_name)
        if in_black:
            if IR_lines[i-1].startswith('; Function'):
                mark_lines[i-1] = 0
            in_func_flag = 0
        mark_lines[i] = in_func_flag
        if line.startswith('}'):
            in_func_flag = 1

        if f_name == '':
            continue
        else:
            # print(in_black, f_name)
            if not in_black:
                func_count += 1
            else:
                removed_funcs.append(f_name)
    # print("white functions:", func_count)
    new_txt = ''
    for i in range(len(IR_lines)):
        line = IR_lines[i]
        if mark_lines[i] != 0:
            new_txt += line + '\n'
    new_txt = trim(new_txt, removed_funcs)
    return new_txt


def trim(txt: str, removed_funcs: list):
    lines = txt.split('\n')
    meta_data_list = []
    for line in lines:
        for func in removed_funcs:
            if func in line and line.startswith('!'):
                reg = r'(![0-9]+) = !\{.+\}'
                match_obj = re.match(reg, line)
                if not match_obj:
                    continue
                var_name = match_obj.group(1)
                meta_data_list.append(var_name)
    new_txt = ''
    for line in lines:
        for func in removed_funcs:
            reg = r'[^0-9a-zA-Z_]+(' + func + r')[^0-9a-zA-Z_]+'
            search_obj = re.search(reg, line+'\n')
            if search_obj:
                line = ''
                break

        for var in meta_data_list:
            if var in line:
                line = line.replace('!remill.function.tie '+var, '')
                break

        if line.startswith('@') and 'internal constant' in line and 'mcsema_attach_call' in line:
            line = ''

        new_txt += line + '\n'
    return new_txt

llvm_as = '/home/lifter/Documents/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-as {} -o {}'
def prune_mcsema():
    global project_dir
    rootdir = '/home/lifter/ncc/data/result/mcsema'
    start_flag = False
    for home, dirs, files in os.walk(rootdir):
        files.sort()
        for filename in files:
            if filename.endswith('.ll') and not filename.endswith('.out.ll'):

                if home.endswith('/51') and filename.startswith('19.'):
                    start_flag = True
                if not start_flag:
                    continue

                print(os.path.join(home, filename))
                out_file = filename[:-3] + ".out.ll"
                project_dir = home

                in_file = os.path.join(home, filename)
                out_file = os.path.join(home, out_file)
                new_txt = prune(in_file)
                write_to_file(new_txt, out_file)

                status, output = cmd(llvm_as.format(out_file, filename[:-3] + ".out.bc"))
                if status != 0:
                    print("error\n", output)


def write_to_file(txt, f_name):
    f = open(f_name, 'w')
    f.write(txt)
    f.close()


def clean():
    global project_dir
    rootdir = '/home/lifter/ncc/data/result/mcsema'
    for home, dirs, files in os.walk(rootdir):
        files.sort()
        for filename in files:
            if filename.endswith('.bc') or (filename.endswith('.ll') and not filename.endswith('.out.ll')):

                print(os.path.join(home, filename))
                project_dir = home

                status, output = cmd('rm '+filename)
                if status != 0:
                    print(output)


if __name__ == '__main__':
    # prune_mcsema()
    clean()
    '''
    print("13.ll")
    new_txt = prune('/home/lifter/ncc/data/result/mcsema/1/13.ll')
    write_to_file(new_txt, '13_new.ll')

    print("14.ll")
    new_txt = prune('/home/lifter/ncc/data/result/mcsema/1/14.ll')
    write_to_file(new_txt, '14_new.ll')

    print("17.ll")
    new_txt = prune('/home/lifter/ncc/data/result/mcsema/1/17.ll')
    write_to_file(new_txt, '17_new.ll')

    print("18.ll")
    new_txt = prune('/home/lifter/ncc/data/result/mcsema/1/18.ll')
    write_to_file(new_txt, '18_new.ll')
    '''
