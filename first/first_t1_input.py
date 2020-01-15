
import nibabel as nib
import numpy as np
import os
import pandas as pd
import argparse
import subprocess
from subprocess import check_call
from glob import glob





def run_first(t1):
    t1_file = t1.split("/")[-1]
    output_dir = t1.split(t1_file)[0].replace("/alignment/", "") + '/first/'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    T1_basename = output_dir +'/'+ t1_file.split(".nii.gz")[0]
    t1_reorient = output_dir +'/'+ t1_file.replace(".nii.gz", "_reorient.nii.gz")
    print(t1_file, output_dir)
    
    flirt_output = output_dir + '/flirt_output.mat'

    check_call(['fslreorient2std',  t1, t1_reorient])
    check_call(['first_flirt', t1_reorient, output_dir + '/flirt_output'])


    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '30', '-o',output_dir + '/R_Caud_first',\
                '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/intref_thal/R_Caud.bmv', '-intref', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/R_Thal_05mm.bmv'])
    check_call(['first_boundary_corr', '-s', output_dir+'/R_Caud_first', '-o', output_dir+ '/R_Caud_corr', '-i', t1_reorient, '-b', 'fast'])

    
    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '30', '-o', output_dir + '/L_Caud_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/intref_thal/L_Caud.bmv', '-intref', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/L_Thal_05mm.bmv'])
    check_call(['first_boundary_corr', '-s', output_dir+'/L_Caud_first', '-o', output_dir+'/L_Caud_corr', '-i', t1_reorient, '-b', 'fast'])

    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '40', '-o', output_dir + '/R_Thal_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/R_Thal_05mm.bmv'])
    check_call(['first_boundary_corr', '-s',output_dir+ '/R_Thal_first', '-o', output_dir+'/R_Thal_corr', '-i', t1_reorient, '-b', 'none'])

    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '40', '-o', output_dir +'/L_Thal_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/L_Thal_05mm.bmv'])
    check_call(['first_boundary_corr', '-s', output_dir+'/L_Thal_first', '-o', output_dir+'/L_Thal_corr', '-i', t1_reorient, '-b', 'none'])

    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '30', '-o', output_dir + '/R_Puta_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/R_Puta_05mm.bmv'])
    check_call(['first_boundary_corr', '-s',output_dir+ '/R_Puta_first', '-o', output_dir+'/R_Puta_corr', '-i', t1_reorient, '-b', 'none'])

    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '30', '-o', output_dir +'/L_Puta_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/L_Puta_05mm.bmv'])
    check_call(['first_boundary_corr', '-s', output_dir+'/L_Puta_first', '-o', output_dir+'/L_Puta_corr', '-i', t1_reorient, '-b', 'none'])

    check_call(['run_first', '-i', t1_reorient, '-t', flirt_output, '-n', '30', '-o', output_dir + '/L_Puta_first', '-m', '/netopt/rhel7/fsl/data/first/models_336_bin/05mm/L_Puta_05mm.bmv'])
    check_call(['first_boundary_corr', '-s', output_dir+'/L_Puta_first', '-o', output_dir+'/L_Puta_corr', '-i', t1_reorient, '-b', 'none'])
    
    check_call(['fslmerge', '-t', T1_basename+'_all_none_firstseg', output_dir+ '/R_Caud_corr', output_dir +'/L_Caud_corr', output_dir +'/R_Thal_corr',\
                output_dir +'/L_Thal_corr', output_dir+'/R_Puta_corr',output_dir+ '/L_Puta_corr'])
    check_call(['fslmerge', '-t', T1_basename+'_all_none_origsegs', output_dir +'/R_Caud_first',\
                output_dir+'/L_Caud_first',output_dir+'/R_Thal_first',output_dir+'/L_Thal_first',output_dir+'/R_Puta_first',output_dir+'/L_Puta_first'])
    check_call(['first_mult_bcorr', '-i', t1_reorient, '-u', T1_basename+'_all_none_origsegs', '-c', T1_basename+'_all_none_firstseg', '-o', T1_basename+'_all_none_firstseg'])
    #first_segmentation = glob.glob(current_location+'/*all_none_firstseg*')[0]
    #orig_segmentation = glob.glob(current_location+'/*all_none_origsegs*')[0]
    #t1_reorient = glob.glob(current_location+'/*reorient*')[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code runs first outside pbr')
    parser.add_argument('-i', help = 'The entire path of the T1 file')
    parser.add_argument
    args = parser.parse_args()
    t1 = args.i
    run_first(t1)
