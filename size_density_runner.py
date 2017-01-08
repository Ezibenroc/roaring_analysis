#! /usr/bin/env python3
from utils import *
import argparse
import csv
import random

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

class DiscreteSampler:
    def __init__(self, values):
        assert len(values) > 0
        self.values = values

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.values)

    def sample(self):
        return random.choice(self.values)

    def min(self):
        if type(self.values) == range: # min function iterate on all the values...
            return self.values.start
        else:
            return min(self.values)

    def max(self):
        if type(self.values) == range: # min function iterate on all the values...
            return self.values.stop-1
        else:
            return max(self.values)

class ContinuousSampler:
    def __init__(self, start, stop):
        assert start <= stop
        self.start = start
        self.stop = stop

    def __str__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.start, self.stop)

    def sample(self):
        return random.random()*(self.stop-self.start)+self.start

    def min(self):
        return self.start

    def max(self):
        return self.stop

LIST_SEP  = ','
RANGE_SEP = ':'

def parse_sample(string, number_cls):
    if RANGE_SEP in string:
        if LIST_SEP in string:
            error('Cannot mix ranges and lists. Got %s.' % string)
        start, stop = parse_range(string, number_cls)
        if number_cls is int:
            return DiscreteSampler(range(start, stop+1))
        else:
            assert number_cls is float
            return ContinuousSampler(start, stop)
    else:
        return DiscreteSampler(parse_list(string, number_cls))

def parse_list(string, number_cls):
    splitted = string.split(LIST_SEP)
    return [parse_number(x, number_cls) for x in splitted]

def parse_range(string, number_cls):
    splitted = string.split(RANGE_SEP)
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
    if density.max() > 1 or density.min() <= 0:
        error('Density must be in ]0, 1], got density=%s.' % (density,))
    if size.min() <= 0:
        error('Size must be positive, got size=%s.' % (size,))
    if size.max()/density.min() >= 2**32:
        error('This size/density combination will yield to non 32 bits integers, got size=%s and density=%s.' % (size, density))

def run_exp(csv_writer, args):
    s1 = args.size1.sample()
    d1 = args.density1.sample()
    s2 = args.size2.sample()
    d2 = args.density2.sample()
    u1 = int(s1/d1)
    u2 = int(s2/d2)
    time = run(size1=s1, universe1=u1, size2=s2, universe2=u2, copy_on_write=args.cow, run_containers=args.run)
    csv_writer.writerow((time,
        s1, d1, u1, s2, d2, u2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Experiment runner for CRoaring')
    parser.add_argument('-n', '--nb_runs', type=int,
            default=1000, help='Number of experiments to perform.')
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('--size1', type = lambda s: parse_sample(s, int),
            required=True, help='Size(s) of the first roaring bitmap.')
    required_named.add_argument('--size2', type = lambda s: parse_sample(s, int),
            required=True, help='Size(s) of the second roaring bitmap.')
    required_named.add_argument('--density1', type = lambda s: parse_sample(s, float),
            required=True, help='Density of the first roaring bitmap.')
    required_named.add_argument('--density2', type = lambda s: parse_sample(s, float),
            required=True, help='Density of the second roaring bitmap.')
    parser.add_argument('--gcc', dest='gcc', action='store_true', help='Enable GCC optimization.')
    parser.add_argument('--no-gcc', dest='gcc', action='store_false', help='Disable GCC optimization.')
    parser.set_defaults(gcc=True)
    parser.add_argument('--avx', dest='avx', action='store_true', help='Enable AVX optimization.')
    parser.add_argument('--no-avx', dest='avx', action='store_false', help='Disable AVX optimization.')
    parser.set_defaults(avx=True)
    parser.add_argument('--amalg', dest='amalg', action='store_true', help='Enable amalgamation optimization.')
    parser.add_argument('--no-amalg', dest='amalg', action='store_false', help='Disable amalgamation optimization.')
    parser.set_defaults(amalg=True)
    parser.add_argument('--cow', dest='cow', action='store_true', help='Enable copy on write optimization.')
    parser.add_argument('--no-cow', dest='cow', action='store_false', help='Disable copy on write optimization.')
    parser.set_defaults(cow=True)
    parser.add_argument('--run', dest='run', action='store_true', help='Enable run containers optimization.')
    parser.add_argument('--no-run', dest='run', action='store_false', help='Disable run containers optimization.')
    parser.set_defaults(run=True)
    parser.add_argument('csv_file', type=str,
            default=None, help='CSV file, to write the raw results.')
    args = parser.parse_args()
    check_params(args.size1, args.density1)
    check_params(args.size2, args.density2)
    print_blue('Parameters:')
    print_blue('\tCSV file                    : %s' % (args.csv_file,))
    print_blue('\tsize1                       : %s' % (args.size1,))
    print_blue('\tsize2                       : %s' % (args.size2,))
    print_blue('\tdensity1                    : %s' % (args.density1,))
    print_blue('\tdensity2                    : %s' % (args.density2,))
    print_blue('\tGCC optimization            : %s' % (args.gcc,))
    print_blue('\tAVX optimization            : %s' % (args.avx,))
    print_blue('\tAmalgamation optimization   : %s' % (args.amalg,))
    print_blue('\tRun containers optimization : %s' % (args.run,))
    print_blue('\tCopy on write optimization  : %s' % (args.cow,))

    with open(args.csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(('time',
            'size1', 'density1', 'universe1', 'size2', 'density2',  'universe2'))
        init_directory(BUILD_DIR)
        compile_exec(amalgamation=args.amalg, gcc_optimization=args.gcc,
                    avx_enabled=args.avx)
        for i in range(args.nb_runs):
            print_green('\t\t\t\t\t%5d/%d' % (i, args.nb_runs))
            run_exp(csv_writer, args)
            print('')
