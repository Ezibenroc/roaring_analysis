#! /usr/bin/env python3

import os
import shutil
from subprocess import Popen, PIPE, DEVNULL
import sys
import random

ROARING_DIR = 'CRoaring'
BUILD_DIR = 'build'

BLUE_STR = '\033[1m\033[94m'
GREEN_STR = '\033[1m\033[92m'
RED_STR = '\033[1m\033[91m'
END_STR = '\033[0m'

def print_color(msg, color):
    print('%s%s%s' % (color, msg, END_STR))

def print_blue(msg):
    print_color(msg, BLUE_STR)

def print_green(msg):
    print_color(msg, GREEN_STR)

def error(msg):
    sys.stderr.write('%sERROR: %s%s\n' % (RED_STR, msg, END_STR))
    sys.exit(1)

def run_command(args):
    print_blue('%s' % ' '.join(args))
    process = Popen(args, stdout=PIPE)
    output = process.communicate()
    if process.wait() != 0:
        error('with command: %s' % ' '.join(args))
    return output[0]

def init_directory(dirname):
    shutil.rmtree(dirname, ignore_errors=True)
    os.mkdir(dirname)
    os.chdir(dirname)

def compile_library_make(gcc_optimization, avx_enabled):
    options = []
    if not gcc_optimization:
        options.extend(['-DCMAKE_BUILD_TYPE=Debug'])
    if not avx_enabled:
        options.extend(['-DDISABLE_AVX=ON'])
    run_command(['cmake', *options, os.path.join('..', ROARING_DIR)])
    run_command(['make', '-j', '4'])
    shutil.copytree(os.path.join('..', ROARING_DIR, 'include', 'roaring'), 'roaring')

def compile_library_amalgamation(gcc_optimization, avx_enabled):
    options = []
    if gcc_optimization:
        options.extend(['-O3'])
    else:
        options.extend(['-O0'])
    if not avx_enabled:
        options.extend(['-DDISABLE_AVX=ON'])
    run_command(['bash', os.path.join('..', ROARING_DIR, 'amalgamation.sh')])
    os.mkdir('roaring')
    shutil.copy('roaring.h', 'roaring')
    run_command(['cc', *options, '-march=native', '-std=c11', '-shared', '-o', 'libroaring.so', '-fPIC', 'roaring.c'])

def compile_exec(amalgamation, gcc_optimization, avx_enabled):
    if amalgamation:
        compile_library_amalgamation(gcc_optimization, avx_enabled)
    else:
        compile_library_make(gcc_optimization, avx_enabled)
    options = []
    if gcc_optimization:
        options.extend(['-O3'])
    else:
        options.extend(['-O0'])
    shutil.copy(os.path.join('..', 'roaring_op.c'), '.')
    run_command(['cc', *options, '-std=c11', '-Wall', '-o', 'roaring_op', 'roaring_op.c', '-lroaring', '-L', '.', '-I', '.'])

def run(size1, universe1, size2, universe2, copy_on_write, run_containers):
    assert size1 in range(0, 2**32)
    assert universe1 in range(0, 2**32)
    assert size2 in range(0, 2**32)
    assert universe2 in range(0, 2**32)
    args = ['./roaring_op',
            str(size1),
            str(universe1),
            str(size2),
            str(universe2),
            str(int(copy_on_write)),
            str(int(run_containers))]
    output = run_command(args)
    return float(output)
