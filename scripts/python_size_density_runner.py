#! /usr/bin/env python3
import random
import time
import argparse
import sys
import csv
from utils import *
from samplers import *

def generate_dataset(dataset_size, dataset_universe_size):
    return random.sample(range(dataset_universe_size), dataset_size)

def run(cls, op, values1, values2):
    left = cls(values1)
    right = cls(values2)
    t = time.time()
    result = op(left, right)
    return time.time()-t

def shuffle(l): # random.shuffle is an inplace operation
    return random.sample(l, len(l))

def run_exp(csv_writer, args, classes, op):
    s1 = args.size1.sample()
    d1 = args.density1.sample()
    s2 = args.size2.sample()
    d2 = args.density2.sample()
    u1 = int(s1/d1)
    u2 = int(s2/d2)
    values1 = generate_dataset(s1, u1)
    values2 = generate_dataset(s2, u2)
    for class_name, cls in shuffle(classes.items()):
        time = run(cls, op, values1, values2)
        csv_writer.writerow((class_name, time,
            s1, d1, u1, s2, d2, u2))

def compile_all():
    init_directory(BUILD_DIR)
    compile_library_amalgamation(True, True)
    os.chdir(os.path.join('..', 'CyRoaring'))
    run_command(['make', '-j', '4'])
    os.chdir('..')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Experiment runner for Pyroaring')
    parser.add_argument('-n', '--nb_runs', type=int,
            default=1000, help='Number of experiments to perform.')
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('--size1', type = lambda s: parse_sample(s, int),
            required=True, help='Sizes of the first roaring bitmap.')
    parser.add_argument('--size2', type = lambda s: parse_sample(s, int),
            help='Sizes of the second roaring bitmap. If not specified, the same random values than for the first roaring bitmap will be used.')
    required_named.add_argument('--density1', type = lambda s: parse_sample(s, float),
            required=True, help='Densities of the first roaring bitmap.')
    parser.add_argument('--density2', type = lambda s: parse_sample(s, float),
            help='Densities of the second roaring bitmap. If not specified, the same random values than for the first roaring bitmap will be used.')
    parser.add_argument('csv_file', type=str,
            default=None, help='CSV file, to write the raw results.')
    args = parser.parse_args()
    if args.size2 is None:
        args.size2 = CopySampler(args.size1)
    if args.density2 is None:
        args.density2 = CopySampler(args.density1)
    check_params(args.size1, args.density1)
    check_params(args.size2, args.density2)
    print('Parameters:')
    print('\tCSV file                    : %s' % (args.csv_file,))
    print('\tsize1                       : %s' % (args.size1,))
    print('\tsize2                       : %s' % (args.size2,))
    print('\tdensity1                    : %s' % (args.density1,))
    print('\tdensity2                    : %s' % (args.density2,))

    compile_all()

    sys.path.append('PyRoaring') # assuming the script is ran from the root directory of the repository
    sys.path.append('CyRoaring') # assuming the script is ran from the root directory of the repository
    from pyroaring import BitMap as PyRoaring
    from roaringbitmap import RoaringBitmap as CyRoaring
    from sortedcontainers import SortedSet
    classes = {'set': set, 'pyroaring': PyRoaring, 'cyroaring': CyRoaring, 'sortedset': SortedSet}
    op = lambda x, y: x|y
    with open(args.csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(('class', 'time',
            'size1', 'density1', 'universe1', 'size2', 'density2',  'universe2'))
        for i in range(args.nb_runs):
            print_green('\t\t\t\t\t%5d/%d' % (i, args.nb_runs))
            run_exp(csv_writer, args, classes, op)
            print('')
