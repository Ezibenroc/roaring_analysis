#! /usr/bin/env python3

import os
import shutil
from subprocess import Popen, PIPE, DEVNULL
import sys
import random
import argparse
import csv
import itertools

ROARING_DIR = 'CRoaring'
BUILD_DIR = 'build'
NB_FACTORS = 9

BLUE_STR = '\033[1m\033[94m'
GREEN_STR = '\033[1m\033[92m'
END_STR = '\033[0m'



class CommandError(Exception):
    pass

def print_color(msg, color):
    print('%s%s%s' % (color, msg, END_STR))

def print_blue(msg):
    print_color(msg, BLUE_STR)

def print_green(msg):
    print_color(msg, GREEN_STR)

def error(msg):
    sys.stderr.write('ERROR: %s\n' % msg)
    sys.exit(1)

def run_command(args, exit_on_error=True):
    print_blue('%s' % ' '.join(args))
    process = Popen(args, stdout=PIPE)
    output = process.communicate()
    if process.wait() != 0:
        if exit_on_error:
            error('with command: %s' % ' '.join(args))
        else:
            raise CommandError()
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
    args = ['./roaring_op',
            str(size1),
            str(universe1),
            str(size2),
            str(universe2),
            str(int(copy_on_write)),
            str(int(run_containers))]
    output = run_command(args, exit_on_error=True)
    return float(output)

def get_sizes(large, dense):
    base_size = 2**20 if large else 2**7
    size = random.randint(base_size-10, base_size+10)
    base_universe = 3*size//2 if dense else (2**6)*size
    universe = random.randint(base_universe, base_universe+10)
    return size, universe

def compile_and_run(csv_writer,
        large1, dense1, large2, dense2,
        copy_on_write, run_containers,
        amalgamation, gcc_optimization, avx_enabled):
    init_directory(BUILD_DIR)
    compile_exec(amalgamation, gcc_optimization, avx_enabled)
    while True:
        try:
            size1, universe1 = get_sizes(large1, dense1)
            size2, universe2 = get_sizes(large2, dense2)
            time = run(size1, universe1, size2, universe2, copy_on_write, run_containers)
            break
        except CommandError:
            continue
    csv_writer.writerow((time,
        large1, dense1, large2, dense2,
        copy_on_write, run_containers,
        amalgamation, gcc_optimization, avx_enabled,
        size1, universe1, size2, universe2))
    os.chdir('..')

def generate_experiments(nb):
    all_values = list(itertools.product ([False, True], repeat = NB_FACTORS))
    experiments = []
    while len(experiments) < nb:
        experiments.extend(random.sample(all_values, min(len(all_values), nb-len(experiments))))
    return experiments


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Experiment runner for CRoaring')
    parser.add_argument('-n', '--nb_runs', type=int,
            default=2**NB_FACTORS, help='Number of experiments to perform.')
    parser.add_argument('csv_file', type=str,
            default=None, help='CSV file, to write the raw results.')
    args = parser.parse_args()

    experiments = generate_experiments(args.nb_runs)

    with open(args.csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(('time',
            'large1', 'dense1', 'large2', 'dense2',
            'copy_on_write', 'run_containers',
            'amalgamation', 'gcc_optimization', 'avx_enabled',
            'size1', 'universe1', 'size2', 'universe2'))
        for i, exp in enumerate(experiments):
            print_green('\t\t\t\t\t%5d/%d' % (i, args.nb_runs))
            compile_and_run(csv_writer, *exp)
            print('')
