from __future__ import division, print_function
import os
import argparse
from filterbank import read_header as filterbank__read_header
from sigproc import samples_per_file as sigproc__samples_per_file

import subprocess

AMBER_SETUP_PATH = '/home/vohl/AMBER_setup/'

OPTIONS_snr_mom_sigmacut_tdsc = [
    'opencl_platform', 'opencl_device', 'device_name', 'rfim', 'dm', 'sync', 'beams', 'width', 'integration_file', 'integration_steps',
    'synthesized_beams', 'channel_bandwidth', 'print', 'snr_mom_sigmacut', 'padding_file',
    'zapped_channels', 'subband_dedispersion', 'dedispersion_stepone_file', 'dedispersion_steptwo_file',
    'max_std_file', 'mom_stepone_file',
    'mom_steptwo_file', 'output', 'subbands', 'dms', 'dm_first', 'dm_step', 'subbanding_dms',
    'subbanding_dm_first', 'subbanding_dm_step', 'threshold', 'sigproc', 'stream', 'header',
    'data', 'batches', 'channel_bandwidth', 'min_freq', 'channels', 'samples', 'sampling_time',
    'compact_results',
    'time_domain_sigma_cut', 'time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration',
    'output'
]

OPTIONS = {"snr_mom_sigmacut_tdsc": OPTIONS_snr_mom_sigmacut_tdsc}

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
    return directory
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

def launch_amber(amber_mode='snr_mom_sigmacut_tdsc',
                 base_name='scenario_3_partitions',
                 input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                 scenario_file='/home/vohl/software/AMBER/scenario/3_dms_partitions/12500/scenario_3_partitions_step1_12500.sh',
                 config_path='/home/vohl/software/AMBER/install/scenario_3_partitions_step1_12500/',
                 cpu_id=1,
                 snrmin=8,
                 output_dir='/home/vohl/data/'):
    # print ("Scenario:", scenario_file)
    # Get scenario
    scenario_dict = parse_scenario_to_dictionary(scenario_file)

    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # COLLECT INFO FROM FILTERBANK
    header, header_size = filterbank__read_header(input_file)
    nbatch = sigproc__samples_per_file(input_file, header, header_size)//1000

    # Get amber's INSTALL_ROOT variable state
    conf_dir_base = os.environ['INSTALL_ROOT']

    # Pin down amber's to cpu id 'cpu_id'
    command = ['taskset', '-c', str(cpu_id),
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
        elif option == 'output':
            command.append(
                check_path_ends_with_slash(
                    check_directory_exists(
                        "%s%s%s%s" % (
                            output_dir,
                            base_name,
                            '_step_',
                            str(cpu_id+1)
                        )
                    )
                )
            )

        elif option == 'zapped_channels':
            pass
        else:
            try:
                command.append(scenario_dict[option.upper()])
            except KeyError:
                # This option doesn't require any input
                pass

    c = ''
    for v in command:
        c += '%s ' % (v)
    c += ' &'
    print ('Command:', c)
    print ()

    # Launch amber, and detach from the process so it runs by itself
    subprocess.Popen(command, preexec_fn=os.setpgrp)

def test_amber_run(amber_mode='snr_mom_sigmacut_tdsc',
                   input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                   n_cpu=3,
                   base_name='tuning_halfrate_3GPU_goodcentralfreq',
                   base_scenario_path='/home/vohl/software/AMBER/scenario/',
                   scenario_files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
                   snrmin=8,
                   base_config_path='/home/vohl/software/AMBER/configuration/',
                   config_repositories=[
                        'tuning_halfrate_3GPU_goodcentralfreq_step1',
                        'tuning_halfrate_3GPU_goodcentralfreq_step2',
                        'tuning_halfrate_3GPU_goodcentralfreq_step3']):
    for cpu_id in range(n_cpu):
        launch_amber (
            amber_mode='snr_mom_sigmacut_tdsc',
            base_name=base_name,
            input_file=input_file,
            scenario_file='%s%s%s' % (
               check_path_ends_with_slash(base_scenario_path),
               check_path_ends_with_slash(base_name),
               scenario_files[cpu_id],
            ),
            config_path='%s%s' % (
                check_path_ends_with_slash(base_config_path),
                check_path_ends_with_slash(config_repositories[cpu_id]),
            ),
            cpu_id=cpu_id,
            snrmin=snrmin
        )

def tune_amber(scenario_file='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/tuning_1.sh',
               config_path='/home/vohl/software/AMBER/configuration/tuning_halfrate_3GPU_goodcentralfreq_step1'):
    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # Define command
    command = [AMBER_SETUP_PATH + 'amber.sh', 'tune', scenario_file, config_path]

    # Launch amber tuning, and detach from the process so it runs by itself
    subprocess.Popen(command, preexec_fn=os.setpgrp)
    # os.system([for c in command print (c),][0] + '&' )

def test_tune(base_scenario_path='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/',
              base_name='tuning_halfrate_3GPU_goodcentralfreq',
              scenario_files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
              config_path='/home/vohl/software/AMBER/configuration/'):

    base_scenario_path=check_path_ends_with_slash(base_scenario_path)
    i = 1
    for file in scenario_files:
        input_file = base_scenario_path+'tuning_'+str(i)+'.sh'
        output_dir = config_path+base_name+'_step'+str(i)

        print (i, input_file, output_dir)
        print ()

        output_dir = check_directory_exists(output_dir)

        tune_amber(input_file, output_dir)
        i+=1

if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--input_dir', help="Repository of input files")
    #
    # args = parser.parse_args()
    # kwargs = check_defaults(**vars(args))

    test_amber_run(    amber_mode='snr_mom_sigmacut_tdsc',
                       input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                       n_cpu=3,
                       base_name='tuning_halfrate_3GPU_goodcentralfreq',
                       base_scenario_path='/home/vohl/software/AMBER/scenario/',
                       scenario_files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
                       snrmin=8,
                       base_config_path='/home/vohl/software/AMBER/configuration/'    )
