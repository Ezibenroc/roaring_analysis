#! /usr/bin/env python3
from utils import *
from samplers import *
import argparse
import csv

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
            required=True, help='Sizes of the first roaring bitmap.')
    parser.add_argument('--size2', type = lambda s: parse_sample(s, int),
            help='Sizes of the second roaring bitmap. If not specified, the same random values than for the first roaring bitmap will be used.')
    required_named.add_argument('--density1', type = lambda s: parse_sample(s, float),
            required=True, help='Densities of the first roaring bitmap.')
    parser.add_argument('--density2', type = lambda s: parse_sample(s, float),
            help='Densities of the second roaring bitmap. If not specified, the same random values than for the first roaring bitmap will be used.')
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
    print('\tGCC optimization            : %s' % (args.gcc,))
    print('\tAVX optimization            : %s' % (args.avx,))
    print('\tAmalgamation optimization   : %s' % (args.amalg,))
    print('\tRun containers optimization : %s' % (args.run,))
    print('\tCopy on write optimization  : %s' % (args.cow,))

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
