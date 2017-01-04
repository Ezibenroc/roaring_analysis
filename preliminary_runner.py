#! /usr/bin/env python3
from utils import *
import argparse
import csv
import itertools

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
    size1, universe1 = get_sizes(large1, dense1)
    size2, universe2 = get_sizes(large2, dense2)
    time = run(size1, universe1, size2, universe2, copy_on_write, run_containers)
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
