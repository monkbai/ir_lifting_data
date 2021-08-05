# -*- coding: utf-8 -*-

from keras.preprocessing.text import Tokenizer
import pickle
import sys


def read_ops_file(file_path):
    with open(file_path, 'r') as f:
        opcodes = f.read()
        opcodes = opcodes.replace('\n', ' ')
        opcodes = opcodes.replace('00', 'nop')
        opcodes = opcodes.replace('...', ' ')
        return opcodes


def build_tokenizer(files: list):
    tokenizer = Tokenizer(num_words=400, split=' ', char_level=False, filters='\n\t\\;.0123456789')
    opcodes = []
    for f in files:
        opcodes.append(read_ops_file(f))
    tokenizer.fit_on_texts(opcodes)
    return tokenizer


def save_tokenizer(tokenizer, dump_file):
    with open(dump_file, 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    files = sys.argv[1:]
    tokenizer = build_tokenizer(files)
    save_tokenizer(tokenizer, 'opcode_tokenizer')

