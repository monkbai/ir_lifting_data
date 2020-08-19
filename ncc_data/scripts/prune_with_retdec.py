import os
import re

retdec_result_dir = '/home/lifter/ncc/data/result/clang_retdec'

define_reg_str = 'define ([^@]| )*? @([0-9a-zA-Z_]+)\(.*\).* \{(.|\s)*?\}'

def get_func_name_list(retdec_txt):
    func_reg_str = define_reg_str
    result = re.finditer(func_reg_str, retdec_txt)
    func_name_list = []
    for match in result:
        func_name = match.group(2)
        func_name_list.append(func_name)
    return func_name_list


def delete_funcs(ir_txt: str, keep_func_name_list: list):
    func_reg_str = define_reg_str + '\n'
    pattern = re.compile(func_reg_str)
    result = pattern.finditer(ir_txt)
    func_name_list = []
    new_txt = ir_txt
    for match in result:
        func_name = match.group(2)
        delete_flag = True
        for keep_name in keep_func_name_list:
            name_reg_str = 'sub_[0-9a-f]+_'+keep_name
            match_obj = re.match(name_reg_str, func_name)
            if match_obj:
                delete_flag = False
        if delete_flag:
            new_txt = new_txt.replace(match.group(), '')
    new_txt = re.sub('; Function Attrs:.*\n\n', '', new_txt)
    new_txt = re.sub('; Function Attrs:.*\n', '', new_txt)
    return new_txt


def extract_funcs(ir_txt: str, keep_func_name_list: list):
    func_reg_str = define_reg_str + '\n'
    pattern = re.compile(func_reg_str)
    result = pattern.finditer(ir_txt)
    func_name_list = []
    new_txt = ''
    for match in result:
        func_name = match.group(2)
        delete_flag = True
        for keep_name in keep_func_name_list:
            name_reg_str = 'sub_[0-9a-f]+_' + keep_name
            match_obj = re.match(name_reg_str, func_name)
            if match_obj:
                new_txt += match.group()
                break

    return new_txt


def prune(dir_num: str, filename: str, ir_file: str):
    """ This function is unacceptable slow """
    retdec_ll = os.path.join(retdec_result_dir, dir_num)
    retdec_ll = os.path.join(retdec_ll, filename)
    f = open(retdec_ll, 'r')
    retdec_txt = f.read()
    f.close()

    func_name_list = get_func_name_list(retdec_txt)

    f = open(ir_file, 'r')
    ir_txt = f.read()
    f.close()

    new_txt = delete_funcs(ir_txt, func_name_list)
    return new_txt


def quick_prune(dir_num: str, filename: str, ir_file: str):
    """ This version only try to extract some target function """
    retdec_ll = os.path.join(retdec_result_dir, dir_num)
    retdec_ll = os.path.join(retdec_ll, filename)
    if not os.path.exists(retdec_ll):
        return ''
    f = open(retdec_ll, 'r')
    retdec_txt = f.read()
    f.close()

    func_name_list = get_func_name_list(retdec_txt)

    f = open(ir_file, 'r')
    ir_txt = f.read()
    f.close()

    new_txt = extract_funcs(ir_txt, func_name_list)
    return new_txt


if __name__ == '__main__':
    func_reg_str = 'define ([^@]| )*? @([0-9a-zA-Z_]+)\(.*\).* \{(.|\s)*?\}'
    test_txt = '''define internal %struct.Memory* @_ZN12_GLOBAL__N_1L17HandleUnsupportedEP6MemoryR5State(%struct.Memory* %0, %struct.State* dereferenceable(3376) %1) #0 !remill.function.type !1240 {
  %3 = tail call %struct.Memory* @__remill_sync_hyper_call(%struct.State* nonnull dereferenceable(3376) %1, %struct.Memory* %0, i32 257) #22
  ret %struct.Memory* %3
}'''
    match_obj = re.search(func_reg_str, test_txt)
    if match_obj:
        print(match_obj.group(2))
        print(match_obj.group())
    new_txt = quick_prune('11', '1.out.ll', '/home/lifter/ncc/data/result/mcsema_minus/11/1.ll')
    print(new_txt)
