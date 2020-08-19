import re
import os


def select_wrapper_defi(input_txt: str):
    match_obj = re.search(r"void wrapper\(void\) \{\n(.*\n)+?\}\n\n", input_txt)
    # match_obj = re.search("Retargetable", input_txt)

    new_txt = match_obj.group()
    return new_txt


def prune(input_txt: str):
    new_txt = select_wrapper_defi(input_txt)
    return new_txt


def main(in_file: str, out_file: str):
    f = open(in_file, 'r')
    in_txt = f.read()
    new_txt = prune(in_txt)
    f.close()

    f = open(out_file, 'w')
    f.write(new_txt)
    f.close()


if __name__ == "__main__":
    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/bzip2.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/bzip2.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/gobmk.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/gobmk.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/h264ref.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/h264ref.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/hmmer.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/hmmer.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/sjeng.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/sjeng.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/libquantum.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/libquantum.c')

    main('/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/mcf.c',
         '/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_binrec/binrec_wrappers/mcf.c')
