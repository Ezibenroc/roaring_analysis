#! /usr/bin/env python3

import os
import shutil
from subprocess import Popen
import sys

libname = 'libroaring.so'
ROARING_DIR = 'CRoaring'

BLUE_STR = '\033[1m\033[94m'
END_STR = '\033[0m'

def print_msg(msg):
    print('%s%s%s' % (BLUE_STR, msg, END_STR))

def error(msg):
    sys.stderr.write('ERROR: %s\n' % msg)
    sys.exit(1)

def run_command(args):
    print_msg(' '.join(args))
    process = Popen(args)
    if process.wait() != 0:
        error('with command: %s' % ' '.join(args))
    print('')

def init_directory(dirname):
    shutil.rmtree(dirname, ignore_errors=True)
    os.mkdir(dirname)
    os.chdir(dirname)

def compile_library_make(gcc_optimization, avx_enabled):
    options = []
    if not gcc_optimization:
        options.extend(['-DCMAKE_BUILD_TYPE=Debug', '-DSANITIZE=ON'])
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
    run_command(['cc', *options, '-march=native', '-std=c11', '-shared', '-o', libname, '-fPIC', 'roaring.c'])

def compile(amalgamation, gcc_optimization, avx_enabled, dirname='build'):
    init_directory(dirname)
    if amalgamation:
        compile_library_amalgamation(gcc_optimization, avx_enabled)
    else:
        compile_library_make(gcc_optimization, avx_enabled)
    option = '-O3' if gcc_optimization else '-O0'
    shutil.copy(os.path.join('..', 'roaring_op.c'), '.')
    run_command(['cc', '-Wall', '-o', 'roaring_op', 'roaring_op.c', '-lroaring', '-L', '.', '-I', '.'])
    os.chdir('..')
