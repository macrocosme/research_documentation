from __future__ import division, print_function
import os
import argparse
import filterbank
from sigproc import samples_per_file

import subprocess

AMBER_SETUP_PATH = '/home/vohl/AMBER_setup/'

OPTIONS_snr_mom_sigmacut = [
    'opencl_platform', 'opencl_device', 'device_name', 'sync', 'print', 'snr_mom_sigmacut', 'padding_file',
    'zapped_channels', 'integration_steps', 'integration_file', 'subband_dedispersion',
    'dedispersion_stepone_file', 'dedispersion_steptwo_file', 'max_std_file', 'mom_stepone_file',
    'mom_steptwo_file', 'output', 'subbands', 'dms', 'dm_first', 'dm_step', 'subbanding_dms',
    'subbanding_dm_first', 'subbanding_dm_step', 'threshold', 'sigproc', 'stream', 'header',
    'data', 'batches', 'channel_bandwidth', 'min_freq', 'channels', 'samples', 'sampling_time',
    'compact_results',
    'time_domain_sigma_cut', 'time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration',
]

OPTIONS = {"snr_mom_sigmacut": OPTIONS_snr_mom_sigmacut}

def check_defaults(**kwargs):
    if kwargs['scenario_file'] == None:
        kwargs['scenario_file'] = ''

    return kwargs

def check_path_ends_with_slash(path):
    if path[-1] != '/':
        path = path + '/'
    return path

def check_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def parse_scenario_to_dictionary(scenario_file):
    '''Parse an amber scenario file to a python dictionary

    Parameters
    ----------
        scenario_file: amber scenario file (including path)

    Returns
    -------
        scenario_dict: parsed dictionary
    '''
    scenario_dict = {}
    with open(scenario_file, 'r') as f:
        for line in f:
            if line[0] not in ['!', '#', '\n']:
                param, value = line.replace('\n', '').replace('"', '').split('=')
                scenario_dict[param] = value
    return scenario_dict

def launch_amber(input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
              scenario_file='/home/vohl/software/AMBER/scenario/3_dms_partitions/12500/scenario_3_partitions_step1_12500.sh',
              config_path='/home/vohl/software/AMBER/install/scenario_3_partitions_step1_12500/',
              step_number=1,
              snrmin=8,
              amber_mode='snr_mom_sigmacut'):
    print (scenario_file)
    # Get scenario
    scenario_dict = parse_scenario_to_dictionary(scenario_file)

    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # COLLECT INFO FROM FILTERBANK
    header, header_size = filterbank.read_header(input_file)
    nbatch = samples_per_file(input_file, header, header_size)//1000

    conf_dir_base = os.environ['INSTALL_ROOT']

    command = ['taskset', '-c', step_number,
                    'amber']

    for option in OPTIONS[amber_mode]:
        # First add the option with a dash (e.g. -opencl_platform)
        command.append('-' + option)

        # Then try to fill the input, if applicable
        if '_file' in option:
            command.append(config_path + option.split('_file')[0] + '.conf')
        elif option == 'time_domain_sigma_cut_steps':
            command.append(config_path + 'tdsc_steps.conf')
        elif option == 'time_domain_sigma_cut_configuration':
            command.append(config_path + 'tdsc.conf')
        else:
            try:
                command.append(scenario_dict[option.upper()])
            except KeyError:
                # This option doesn't require any input
                pass

    print (command)
    print ()

    # Launch amber, and detach from the process so it runs by itself
    # subprocess.Popen(command, preexec_fn=os.setpgrp)

def tune_amber(scenario_file='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/tuning_1.sh',
               config_path='/home/vohl/software/AMBER/configuration/tuning_halfrate_3GPU_goodcentralfreq_step1'):
    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # Define command
    command = [AMBER_SETUP_PATH + 'amber.sh', 'tune', scenario_file, config_path]

    # Launch amber tuning, and detach from the process so it runs by itself
    subprocess.Popen(command, preexec_fn=os.setpgrp)

def test_tune(base_scenario_path='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/',
              base_name='tuning_halfrate_3GPU_goodcentralfreq',
              files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
              config_path='/home/vohl/software/AMBER/configuration/'):

    base_scenario_path=check_path_ends_with_slash(base_scenario_path)
    i = 1
    for file in files:
        input_file = base_scenario_path+'tuning_'+str(i)+'.sh'
        output_dir = config_path+base_name+'_step'+str(i)

        print (i, input_file, output_dir)
        print ()

        check_directory_exists(output_dir)

        tune_amber(input_file, output_dir)
        i+=1

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help="Repository of input files")

    args = parser.parse_args()
    kwargs = check_defaults(**vars(args))
