import re
import os


def delete_wrapper_decl(input_txt: str):
    new_txt = re.sub("struct .*_wrapper\(.*\);\n", "", input_txt)
    return new_txt


def delete_wrapper_defi(input_txt: str):
    new_txt = re.sub("struct .*_wrapper\(.*\) \{(.*\n)+?\}\n\n", "", input_txt)
    return new_txt


def delete_ZN_decl(input_txt: str):
    new_txt = re.sub("struct .* _ZN[a-zA-Z0-9_]*\(.*\);\n", "", input_txt)
    return new_txt


def delete_ZN_defi(input_txt: str):
    new_txt = re.sub("struct .* _ZN[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", input_txt)
    return new_txt


def delete_ZL_decl(input_txt: str):
    new_txt = re.sub("struct .* _ZL[a-zA-Z0-9_]*\(.*\);\n", "", input_txt)
    return new_txt


def delete_ZL_defi(input_txt: str):
    new_txt = re.sub("struct .* _ZL[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", input_txt)
    return new_txt


def delete_mcsema_decl(input_txt: str):
    new_txt = re.sub("struct .* __mcsema[a-zA-Z0-9_]*\(.*\);\n", "", input_txt)
    new_txt = re.sub("struct .* __remill[a-zA-Z0-9_]*\(.*\);\n", "", new_txt)
    new_txt = re.sub("void .*__mcsema[a-zA-Z0-9_]*\(.*\);\n", "", new_txt)
    new_txt = re.sub("void .*__remill[a-zA-Z0-9_]*\(.*\);\n", "", new_txt)
    return new_txt


def delete_mcsema_defi(input_txt: str):
    new_txt = re.sub("struct .* __mcsema[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", input_txt)
    new_txt = re.sub("struct .* __remill[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", new_txt)
    new_txt = re.sub("void .*__mcsema[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", new_txt)
    new_txt = re.sub("void .*__remill[a-zA-Z0-9_]*\(.*\) \{(.*\n)+?\}\n\n", "", new_txt)
    return new_txt


def prune(input_txt: str):
    new_txt = delete_wrapper_decl(input_txt)
    new_txt = delete_ZN_decl(new_txt)
    new_txt = delete_ZL_decl(new_txt)
    new_txt = delete_mcsema_decl(new_txt)

    new_txt = delete_wrapper_defi(new_txt)
    new_txt = delete_ZN_defi(new_txt)
    new_txt = delete_ZL_defi(new_txt)
    new_txt = delete_mcsema_defi(new_txt)
    return new_txt


def main():
    for home, dirs, files in os.walk("/home/lifter/Documents/IR_lifter_testing/decompile_test/spec_ir_mcsema_pruned"):
        files.sort()
        for filename in files:

            if filename.endswith('_base.c'):
                c_name = filename[:-6] + 'new.c'
                print(os.path.join(home, filename))
                filename = os.path.join(home, filename)
                c_name = os.path.join(home, c_name)

                f = open(filename, 'r')
                input_txt = f.read()
                f.close()
                new_txt = prune(input_txt)

                f = open(c_name, 'w')
                f.write(new_txt)
                f.close()


if __name__ == "__main__":
    test_str = """void callback_sub_400910__start(void) {
    return;
}

struct struct_Memory * callback_sub_400910__start_wrapper(struct struct_State * a1, int64_t a2, struct struct_Memory * a3) {
    __mcsema_early_init();
    return sub_400910__start(a1, a2, a3);
}

void __mcsema_early_init(void) {
    bool v1 = g22;
    if (v1) {
        return;
    }
    g22 = true;
}
"""
    new_txt = delete_wrapper_defi(test_str)
    print(new_txt)
    main()
