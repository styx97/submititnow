import os.path as osp
import sys
import argparse
import importlib
import submitit

from submititnow import experiment_utils

def get_module_name(src_file: str):
    assert src_file.endswith('.py'), f"'{src_file}' is not a Python source file."
    return '.'.join(src_file.rsplit('.')[0].split('/'))

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src_file', help='Source file to execute')
    
    experiment_utils.add_submitit_params(parser)
    experiment_utils.add_umiacs_params(parser)
    
    args, downstream_args = parser.parse_known_args()
    target_module_name = get_module_name(args.src_file)
    exp_name = args.exp_name or target_module_name
    target_module = importlib.import_module(target_module_name)
    
    module_argparser = target_module.add_arguments()
    module_args = module_argparser.parse_args(downstream_args)
    job_description = args.src_file + ' ' + ' '.join(downstream_args)
    
    experiment = experiment_utils.Experiment(
        exp_name, 
        job_func=target_module.main,
        job_params=[module_args],
        job_desc_function=lambda p: job_description,
        submitit_log_dir=args.submitit_log_dir)
    
    slurm_params = experiment_utils.get_slurm_params(args)
    
    job = experiment.launch(**slurm_params)[0]
    
    print(job.result())
    
    
    
