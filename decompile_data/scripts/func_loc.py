import re
import os

type_reg = "(struct|int32_t|int64_t|int128_t|float64_t|int|char|void)"
func_reg = type_reg + ".* ([a-zA-Z0-9_]+)\(.*\) \{(.*\n)+?\}\n\n"


def find_all_funcs(code_path: str, log_path: str):
    code_txt = open(code_path, 'r').read()

    log_file = open(log_path, 'w')

    pattern = re.compile(func_reg)
    func_list_it = pattern.finditer(code_txt)

    total_line_num = 0
    func_num = 0
    for fun_match in func_list_it:
        fun = fun_match.group()
        line_num = fun.count('\n')
        if line_num == 4:
            continue # skip wrapper function
        total_line_num += line_num
        func_num += 1

        log_file.write("function: " + fun_match.group(2) + "\nLOC: "+str(line_num) + '\n')
    log_file.write("total function count: " + str(func_num) + "\ntotal LOC: " + str(total_line_num) + '\n')
    if (func_num != 0):
        log_file.write("Average Loc: " + str(total_line_num / func_num) + "\n")
    log_file.close()
    return func_num, total_line_num


def handle_all_files(dir_path: str):
    total_func_num = 0
    total_LOC = 0
    for home, dirs, files in os.walk(dir_path):
        files.sort()
        for f in files:
            if not f.endswith('.c') or "gcc" in f or "perlbench" in f:
                continue
            file_path = os.path.join(home, f)
            log_path = os.path.join(home, f + '.log')
            func_num, LOC = find_all_funcs(file_path, log_path)
            total_func_num += func_num
            total_LOC += LOC
    log_file = os.path.join(dir_path, "log.txt")
    log = open(log_file, 'w')
    log.write("total_func_num\n")
    log.write(str(total_func_num)+'\n')
    log.write("total_LOC\n")
    log.write(str(total_LOC) + '\n')
    log.write("Average_LOC\n")
    log.write(str(total_LOC / total_func_num) + '\n')


def main():
    handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_retdec')
    handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_mcsema_pruned')
    handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_mcsema_minus_pruned')
    handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec_')

    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/bzip2')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/gcc')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/gobmk')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/h264ref')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/hmmer')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/libquantum')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/mcf')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/perlbench')
    # handle_all_files('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_clang_8/sjeng')



if __name__ == '__main__':
    main()
