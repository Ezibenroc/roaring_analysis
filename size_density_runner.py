#! /usr/bin/env python3
from utils import *
import argparse
import csv
import random

AVX_ENABLED      = True
GCC_OPTIMIZATION = True
COPY_ON_WRITE    = True
RUN_CONTAINERS   = True
AMALGAMATION     = True

def compile_and_run(csv_writer,
        large1, dense1, large2, dense2,
        copy_on_write, run_containers,
        amalgamation, gcc_optimization, avx_enabled):
    init_directory(BUILD_DIR)
    compile_exec(amalgamation, gcc_optimization, avx_enabled)
    size1, universe1 = get_sizes(large1, dense1)
    size2, universe2 = get_sizes(large2, dense2)
    time = run(size1, universe1, size2, universe2, copy_on_write, run_containers)
    csv_writer.writerow((time,
        large1, dense1, large2, dense2,
        copy_on_write, run_containers,
        amalgamation, gcc_optimization, avx_enabled,
        size1, universe1, size2, universe2))
    os.chdir('..')

def parse_range(string, number_cls):
    splitted = string.split(':')
    if len(splitted) > 2:
        error('Incorrect value for range, got %s.' % string)
    elif len(splitted) == 1:
        value = parse_number(splitted[0], number_cls)
        result = (value, value)
    else:
        result = (parse_number(splitted[0], number_cls), parse_number(splitted[1], number_cls))
    if result[1] < result[0]:
        error('Empty range, got %s.' % string)
    return result

def parse_number(string, number_cls):
    try:
        result = number_cls(string)
    except ValueError:
        error('Incorrect value for %s, got %s.' % (number_cls.__name__, string))
    return result

def check_params(size, density):
    if size[1] * density[1] >= 2**32:
        error('This size/density combination will yield to non 32 bits integers, got size=%s and density=%s.' % (size, density))
    if density[1] > 1 or density[0] <= 0:
        error('Density must be in ]0, 1], got density=%s.' % (density,))

def randfloat(density):
    return random.random()*(density[1]-density[0])+density[0]

def run_exp(csv_writer, size1, density1, size2, density2):
    s1 = random.randrange(size1[0], size1[1]+1)
    d1 = randfloat(density1)
    s2 = random.randrange(size2[0], size2[1]+1)
    d2 = randfloat(density2)
    u1 = int(s1/d1)
    u2 = int(s2/d2)
    time = run(size1=s1, universe1=u1, size2=s2, universe2=u2, copy_on_write=COPY_ON_WRITE, run_containers=RUN_CONTAINERS)
    csv_writer.writerow((time,
        s1, u1, s2, u2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Experiment runner for CRoaring')
    parser.add_argument('-n', '--nb_runs', type=int,
            default=1000, help='Number of experiments to perform.')
    parser.add_argument('-s1', '--size1', type=str,
            default='1024', help='Size(s) of the first roaring bitmap.')
    parser.add_argument('-s2', '--size2', type=str,
            default='1024', help='Size(s) of the second roaring bitmap.')
    parser.add_argument('-d1', '--density1', type=str,
            default='0.5', help='Density of the first roaring bitmap.')
    parser.add_argument('-d2', '--density2', type=str,
            default='0.5', help='Density of the second roaring bitmap.')
    parser.add_argument('csv_file', type=str,
            default=None, help='CSV file, to write the raw results.')
    args = parser.parse_args()

    size1 = parse_range(args.size1, int)
    size2 = parse_range(args.size2, int)
    density1 = parse_range(args.density1, float)
    density2 = parse_range(args.density2, float)
    check_params(size1, density1)
    check_params(size2, density2)
    print_blue('Parameters:')
    print_blue('\tsize1    : %s' % (size1,))
    print_blue('\tsize2    : %s' % (size2,))
    print_blue('\tdensity1 : %s' % (density1,))
    print_blue('\tdensity2 : %s\n' % (density2,))

    with open(args.csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(('time',
            'size1', 'universe1', 'size2', 'universe2'))
        init_directory(BUILD_DIR)
        compile_exec(amalgamation=AMALGAMATION, gcc_optimization=GCC_OPTIMIZATION,
                    avx_enabled=AVX_ENABLED)
        for i in range(args.nb_runs):
            print_green('\t\t\t\t\t%5d/%d' % (i, args.nb_runs))
            run_exp(csv_writer, size1, density1, size2, density2)
            print('')
