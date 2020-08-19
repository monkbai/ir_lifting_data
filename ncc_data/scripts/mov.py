import os

base = "clang_mcsema_minus/"
base = "clang_binrec/"
f1 = ["ir_train", "ir_val", "ir_test"]
f2 = ["train.list", "val.list", "test.list"]

for i in [0, 1, 2]:
    ir = f1[i]
    jr = f2[i]
    os.system("mkdir " + base + ir)

    with open(jr) as f:
        lines = f.readlines()
        for l in lines:
            d = l.split()[0]
            if (os.path.isdir(base + ir + "/" + d) == False):
                os.system("mkdir " + base + ir + "/" + d)
            fn = l.split()[1]
            fn1 = fn.split(".")[0]
            # 1040.out-dis.ll
            # 1040.out.ll
            # 1-1001.ll
            # os.system("cp " + base + d + "/" + fn1 +".out.ll " + base + ir + "/" + d + "/" + fn)
            os.system("cp " + base + d + "/" + d + '-' + fn1 +".ll " + base + ir + "/" + d + "/" + fn1 + ".ll")
