#!/usr/bin/python3
import re
import subprocess
import os

project_dir = "./"


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


debug_info = ''
the_constant = 16
tmp_var_id = 0
type_reg_str = r"([a-z0-9\*]+)"
var_reg_str = r"([a-z0-9_\.\-]+)"

def get_main_vars(debug_info: str):
    main_start = debug_info.find("DW_AT_name        : main")
    main_func = debug_info[main_start:]
    local_vars = main_func.split('<2>')
    local_vars = local_vars[1:-1]
    return local_vars


def parse_vars(var_info: str):
    var_info_lines = var_info.split('\n')
    var_name = ''
    var_loc = ''
    var_type = ''
    for line in var_info_lines:
        if not line.startswith('    '):
            continue
        line = line.strip()[5:].strip()
        first_col = line.find(':')
        info = line[:first_col].strip()
        value = line[first_col+1:].strip()
        if 'DW_AT_name' in info:
            var_name = value
        elif 'DW_AT_location' in info:
            var_loc = value
            loc_offset = int(get_rbp_offset(var_loc))
        elif 'DW_AT_type' in info:
            var_type = value
            var_type = get_var_type(var_type, debug_info)
    # print('name {}, loc {}, rbp offset {}, type {}'.format(var_name, var_loc, loc_offset, var_type))
    return var_name, loc_offset, var_type


def get_rbp_offset(loc_value: str):
    match = re.search('\(DW_OP_breg6 \(rbp\): (-?[0-9]+)\)', loc_value)
    if match:
        return match.group(1)
    return '0'


def get_var_type(type_value: str, debug_info: str):
    type_value = '<' + type_value[3:]
    type_info = debug_info[debug_info.find(type_value)+6:]
    type_info = type_info[:type_info.find('<1>')].strip()
    type_lines = type_info.split('\n')
    if 'DW_TAG_pointer_type' in type_lines[0]:
        return 'pointer'
    for line in type_lines:
        line.strip()
        if 'DW_AT_name' in line:
            return line[line.find(':')+1:].strip()


def replace_var_type(var_item, ll_txt: str):
    reg_str = r"%[0-9a-z_]+_" + str(var_item[1]-the_constant) + r" = alloca i[0-9\*]+"
    match = re.search(reg_str, ll_txt)
    if match:
        old_alloca = match.group()
        new_alloca = old_alloca[:old_alloca.find('alloca')+7]
        if var_item[2] == "pointer":
            new_alloca += "i32*"
        elif var_item[2] == "unsigned long":
            new_alloca += "i64"
        elif var_item[2] == "long":
            new_alloca += "i64"
        elif var_item[2] == "int":
            new_alloca += "i32"
        elif var_item[2] == "char":
            new_alloca += "i8"
        else:
            print("unimplemented")
        ll_txt = ll_txt.replace(old_alloca, new_alloca)
        print("debug: replace var at {}".format(var_item[1]-the_constant))
    return ll_txt


def refine(ll_txt: str):
    status = -1
    while status != 0:
        with open('tmp.ll', 'w') as f:
            f.write(ll_txt)
        status, output = cmd("llvm-as-10 tmp.ll -o tmp.bc")
        if status != 0:
            print(output)
            ll_txt = handle_error(output, ll_txt)
    return ll_txt


def handle_error(err_msg: str, ll_txt: str):
    global tmp_var_id
    err_lines = err_msg.split('\n')
    target_line = err_lines[1]
    if "explicit pointee type doesn't match operand's pointee type" in err_msg:
        match = re.search(r"load ([a-z0-9\*]+), ([a-z0-9\*]+) %([a-z0-9_\.\-]+),", target_line)
        load_type = match.group(1)
        ptr_type = match.group(2)
        ptr_var = match.group(3)
        bitcast_line = "  %tmp_{} = bitcast {} %{} to {}\n".format(tmp_var_id, ptr_type, ptr_var, load_type + '*')
        new_line = target_line.replace(", {} %{}".format(ptr_type, ptr_var),
                                       ", {} %tmp_{}".format(load_type + "*", tmp_var_id))
        tmp_var_id += 1
        ll_txt = ll_txt.replace(target_line, bitcast_line + new_line)
    elif "stored value and pointer type do not match" in err_msg:
        match = re.search(r"store ([a-z0-9\*]+) %([a-z0-9_\.\-]+), ([a-z0-9\*]+) %([a-z0-9_\.\-]+)", target_line)
        store_type = match.group(1)
        store_var = match.group(2)
        ptr_type = match.group(3)
        ptr_var = match.group(4)
        bitcast_line = "  %tmp_{} = bitcast {} %{} to {}\n".format(tmp_var_id, ptr_type, ptr_var, store_type+'*')
        new_line = target_line.replace(", {} %{}".format(ptr_type, ptr_var),
                                       ", {} %tmp_{}".format(store_type+"*", tmp_var_id))
        tmp_var_id += 1
        ll_txt = ll_txt.replace(target_line, bitcast_line+new_line)
    elif "defined with type" in err_msg and "but expected" in err_msg and "call" not in target_line:
        match = re.search(r"'%([a-z0-9_\.\-]+)' defined with type '([a-z0-9\*]+)' but expected '([a-z0-9\*]+)'", err_lines[0])
        var_name = match.group(1)
        new_type = match.group(2)
        old_type = match.group(3)
        a_half = target_line[:target_line.find(',')]
        b_half = target_line[target_line.find(','):]
        if var_name in a_half:
            a_half = a_half.replace(old_type, new_type, 1)
        elif var_name in b_half:
            b_half = b_half.replace(old_type, new_type, 1)
        new_line = a_half + b_half
        ll_txt = ll_txt.replace(target_line, new_line)
    elif "defined with type" in err_msg and "but expected" in err_msg and "call" in target_line:
        match = re.search(r"'%([a-z0-9_\.\-]+)' defined with type '([a-z0-9\*]+)' but expected '([a-z0-9\*]+)'", err_lines[0])
        var_name = match.group(1)
        old_type = match.group(2)
        new_type = match.group(3)
        if '*' in new_type and '*' in old_type:
            prev_line = "  %tmp_{} = bitcast {} %{} to {}\n".format(tmp_var_id, old_type, var_name, new_type)
        elif '*' in new_type and '*' not in old_type:
            prev_line = "  %tmp_{} = inttoptr {} %{} to {}\n".format(tmp_var_id, old_type, var_name, new_type)
        else:
            print('unimplemented')
        new_line = target_line.replace("%{}".format(var_name), "%tmp_{}".format(tmp_var_id))
        tmp_var_id += 1
        ll_txt = ll_txt.replace(target_line, prev_line + new_line)
    else:
        print("unimplemented")
    return ll_txt


def extend(debug_info_path: str, ll_path: str, new_ll_path: str):
    global debug_info, tmp_var_id
    tmp_var_id = 0
    var_list = []

    with open(debug_info_path, 'r') as f:
        debug_info = f.read()
        local_vars = get_main_vars(debug_info)
        # print(local_vars)
        for var in local_vars:
            var_list.append(parse_vars(var))

    with open(ll_path, 'r') as ll_f:
        ll_txt = ll_f.read()
        ll_txt = modify_ALIAS(ll_txt)
        for var_item in var_list:
            ll_txt = replace_var_type(var_item, ll_txt)

    ll_txt = refine(ll_txt)
    with open(new_ll_path, 'w') as new_f:
        new_f.write(ll_txt)
    return ll_txt


def replace_ALIAS_funcs_def(ll_txt: str):
    func_list = ["NOALIAS", "MAYALIAS", "MUSALIAS"]
    for func_name in func_list:
        match = re.search(r'define ([a-z0-9\*]+) @' + func_name +r'\(([a-z0-9\*]+) %([a-z0-9_\.\-]+), ([a-z0-9\*]+) %([a-z0-9_\.\-]+)\)', ll_txt)
        if not match:
            continue
        ret_type = match.group(1)
        type1 = match.group(2)
        var1 = match.group(3)
        type2 = match.group(4)
        var2 = match.group(5)
        ll_txt = ll_txt.replace(match.group(), "define {} @{}(i8* %{}, i8* %{})".format(ret_type, func_name, var1, var2))
    return ll_txt


def replace_ALIAS_funcs_call(ll_txt: str):
    func_list = ["NOALIAS", "MAYALIAS", "MUSALIAS"]
    for func_name in func_list:
        match_iter = re.finditer(r'call ([a-z0-9\*]+) @' + func_name +r'\(([a-z0-9\*]+) %([a-z0-9_\.\-]+), ([a-z0-9\*]+) %([a-z0-9_\.\-]+)\)', ll_txt)
        for match in match_iter:
            ret_type = match.group(1)
            type1 = match.group(2)
            var1 = match.group(3)
            type2 = match.group(4)
            var2 = match.group(5)
            ll_txt = ll_txt.replace(match.group(), "call {} @{}(i8* %{}, i8* %{})".format(ret_type, func_name, var1, var2))
    return ll_txt


def modify_ALIAS(ll_txt: str):
    ll_txt = replace_ALIAS_funcs_def(ll_txt)
    ll_txt = replace_ALIAS_funcs_call(ll_txt)
    return ll_txt


if __name__ == '__main__':
    debug_ll_dir = '/home/lifter/Documents/IR_test_data_aarch64/debin_dbg/auto_extend/debug_retdec_opt/'
    dbg_dir = '/home/lifter/Documents/IR_test_data_aarch64/debin_dbg/auto_extend/debin_output/'
    new_ll_dir = "/home/lifter/Documents/IR_test_data_aarch64/debin_dbg/auto_extend/extended_debug_opt"

    file_count = 0
    for home, dirs, files in os.walk(debug_ll_dir):
        files.sort()
        for filename in files:
            if filename.endswith('.out.ll'):
                # print(os.path.join(home, filename))
                # project_dir = home
                debug_info_name = filename[:-7] + ".debug_info.txt"
                new_ll_name = filename[:-7] + ".debin.ll"
                debug_ll_path = os.path.join(home, filename)
                debug_info_path = os.path.join(dbg_dir, debug_info_name)
                new_ll_path = os.path.join(new_ll_dir, new_ll_name)

                if not os.path.exists(new_ll_path):
                    print(debug_ll_path)
                    extend(debug_info_path, debug_ll_path, new_ll_path)
                file_count += 1
    print("file_count,", file_count)

