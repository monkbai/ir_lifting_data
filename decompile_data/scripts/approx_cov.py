import json

total_goto_num = 0
total_approx_goto_num = 0


def get_func_list(json_file: str):
    f = open(json_file, 'r')
    txt = f.read()
    f.close()

    data = json.loads(txt)
    return data["functions"]


def cal_cov(c_txt: str, func_list):
    total_func_num = 0
    covered_func_num = 0
    for func in func_list:
        func_name = func["name"]
        start_addr = func["startAddr"]
        total_func_num += 1

        if c_txt.find(start_addr) != -1:
            # print(func_name, "covered")
            covered_func_num += 1
        else:
            pass
            # print(func_name, "not")
    print("coverage", covered_func_num/total_func_num)
    return covered_func_num/total_func_num


def main(file_name: str):
    global total_goto_num, total_approx_goto_num
    print(file_name)
    json_file = "/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/retdec_json/{}_base.out.config.json".format(file_name)
    func_list = get_func_list(json_file)

    c_file = '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/{}.c'.format(file_name)
    c_txt = open(c_file, 'r').read()
    cov = cal_cov(c_txt, func_list)
    # print(func_list)

    goto_num = c_txt.count("goto lab")
    print("goto_num", goto_num)
    total_goto_num += goto_num

    approx_goto_num = int(goto_num / cov)
    print("appro_goto_num", approx_goto_num)
    total_approx_goto_num += approx_goto_num


if __name__ == "__main__":
    main('bzip2')
    main('gobmk')
    main('h264ref')
    main('hmmer')
    main('libquantum')
    main('mcf')
    main('sjeng')
    print("total_goto_num", total_goto_num)
    print("total_approx_goto_num", total_approx_goto_num)
