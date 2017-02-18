#! /usr/bin/env python3
from utils import *
import argparse
import csv
import itertools

factors = [
    'large1', 'dense1', 'large2', 'dense2',
    'copy_on_write', 'run_containers',
    'amalgamation', 'gcc_optimization', 'avx_enabled'
]

fixed_factors = {
    'large1'           : True,
    'large2'           : True,
    'gcc_optimization' : True,
}

assert all(fact in factors for fact in fixed_factors)

def get_sizes(large, dense):
    base_size = 2**20 if large else 2**7
    size = random.randint(base_size-10, base_size+10)
    base_universe = 3*size//2 if dense else (2**6)*size
    universe = random.randint(base_universe, base_universe+10)
    return size, universe

def compile_and_run(csv_writer, exp):
    init_directory(BUILD_DIR)
    compile_exec(exp['amalgamation'], exp['gcc_optimization'], exp['avx_enabled'])
    size1, universe1 = get_sizes(exp['large1'], exp['dense1'])
    size2, universe2 = get_sizes(exp['large2'], exp['dense2'])
    time = run(size1, universe1, size2, universe2, exp['copy_on_write'], exp['run_containers'])
    factor_values = [exp[fact] for fact in factors]
    csv_writer.writerow((time,
        *factor_values,
        size1, universe1, size2, universe2))
    os.chdir('..')

def uniquify_dict_list(d_list):
    d_list = set([tuple(d.items()) for d in d_list])
    result = []
    for elt in d_list:
        result.append({key:value for key, value in elt})
    return result

def generate_experiments(nb):
    all_values = list(itertools.product ([False, True], repeat = len(factors)))
    possible_exp = []
    for values in all_values:
        exp = dict(zip(factors, values))
        for fixed_factor, fixed_value in fixed_factors.items():
            exp[fixed_factor] = fixed_value
        possible_exp.append(exp)
    possible_exp = uniquify_dict_list(possible_exp)
    assert len(possible_exp) == 2**(len(factors) - len(fixed_factors))
    experiments = []
    while len(experiments) < nb:
        experiments.extend(random.sample(possible_exp, min(len(possible_exp), nb-len(experiments))))
    return experiments


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Experiment runner for CRoaring')
    parser.add_argument('-n', '--nb_runs', type=int,
            default=2**len(factors), help='Number of experiments to perform.')
    parser.add_argument('csv_file', type=str,
            default=None, help='CSV file, to write the raw results.')
    args = parser.parse_args()

    experiments = generate_experiments(args.nb_runs)

    with open(args.csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(('time',
            *factors,
            'size1', 'universe1', 'size2', 'universe2'))
        for i, exp in enumerate(experiments):
            print_green('\t\t\t\t\t%5d/%d' % (i, args.nb_runs))
            compile_and_run(csv_writer, exp)
            print('')
