import keras
import pickle
import numpy as np
from src.utils.interact_docker import *


tokenizer = None
with open('opcode_tokenizer', 'rb') as _token_file_handle:
    tokenizer = pickle.load(_token_file_handle)


def dumpfile2opcodefile(dump_path, opcode_path):
    with open(dump_path, 'r') as dump_f:
        lines = dump_f.readlines()
        opcodes = []
        for line in lines:
            if '\t' not in line:
                continue
            assemble_code = line.split('\t')[-1]
            opcode = assemble_code.split(' ')[0]
            assert len(opcode) > 0, 'empty option code!'
            if not opcode.endswith('\n'):
                opcode += '\n'
            opcodes.append(opcode)

    with open(opcode_path, 'w') as op_f:
        op_f.writelines(opcodes)


def bin2opcode(bin: str, opcode_path: str):
    base_name = os.path.basename(opcode_path)
    tmp_dump = '/tmp/{}.tmp_dump.s'.format(base_name)
    os.system(OBJDUMP + bin + ' > ' + tmp_dump)
    dumpfile2opcodefile(tmp_dump, opcode_path)


def opcodes2vec(opcodes: str):
    #encode_ops = keras.preprocessing.text.one_hot(text=opcodes, n=instrs_size)
    tmp_code = tokenizer.texts_to_sequences([opcodes])
    encode_ops = tmp_code[0]
    ops_len = len(encode_ops)
    if ops_len < max_ops_len:
        encode_ops.extend([0 for _ in range(max_ops_len - ops_len)])
    else:
        encode_ops = encode_ops[:max_ops_len]
    return encode_ops
    #encode_ops = tokenizer.texts_to_sequences(opcodes.split())
    #ops_len = len(encode_ops)
    #if ops_len < max_ops_len:
    #    encode_ops.extend([[0] for _ in range(max_ops_len - ops_len)])
    #else:
    #    encode_ops = encode_ops[:max_ops_len]
    #encode_ops = tokenizer.sequences_to_matrix(encode_ops)
    #return encode_ops


def _get_bin_ops(bin_path: str):
    ops_path = bin_path + '.ops'
    bin2opcode(bin_path, ops_path)
    with open(ops_path, 'r') as op_f:
        opcodes = op_f.read()
    return ops_path, opcodes


def bin2state(bin_path: str):
    _, opcodes = _get_bin_ops(bin_path)
    state = opcodes2vec(opcodes)
    return state
