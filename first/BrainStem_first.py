import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import shutil
from subprocess import check_call



def run_first(t1,odir):

    if not os.path.exists(odir):
        os.mkdir(odir)
    if len(glob('{}/*first*'.format(odir))) == 0:


        fname = str(t1).split('/')[-1].split('.nii')[0]
        oname = os.path.join(odir, fname)

        omat = oname+'_to_std_sub'

        flirt_job = ['first_flirt', t1, omat]
        mat_name = omat+'.mat'

        if not os.path.exists(mat_name):
            print(flirt_job)
            check_call(flirt_job)

        imsfirst = []
        imscorr = []
        for s in ['BrStem']:

            modelN = '336'
            bcorr = '1'
            intref = '0'
            if 'BrStem' in s:
                nmodes = '40'
                #bcorr = '0'
            else:
                raise ValueError('The structure {} is not in the structure list'.format(s))

            imfirst = '{}-{}_first'.format(oname, s)
            imsfirst.append(imfirst)

            FSLDIR = '/netopt/fsl5'

            cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                           '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/{}_bin.bmv'.format(FSLDIR, modelN, s)]

            print('\nRunning Segmentation {} with: {}'.format(s,cmd))
            check_call(cmd)

            imcorr = '{}-{}_corr'.format(oname, s)
            imscorr.append(imcorr)

            btype = 'fast'
            if bcorr != '1': btype='none'
            cmd = ['{}/bin/first_boundary_corr'.format(FSLDIR), '-s', imfirst, '-o', imcorr,
                   '-i', t1, '-b', btype]
            print(cmd)
            check_call(cmd)

        cmd = ['{}/bin/fslmerge'.format(FSLDIR), '-t', '{}_all_{}_firstsegs'.format(oname, btype)]


        for imCORR in imscorr:
            if os.path.exists(imCORR + '.nii.gz'):
                cmd.append(imCORR+'.nii.gz')
                print(cmd)

        print(cmd)
        check_call(cmd)

        cmd = ['{}/bin/fslmerge'.format(FSLDIR), '-t', '{}_all_{}_origsegs'.format(oname, btype)]
        for imname in imsfirst:
            if os.path.exists(imname + '.nii.gz'):
                cmd.append(imname+'.nii.gz')
        print(cmd)
        check_call(cmd)

        cmd =  ['{}/bin/first_mult_bcorr'.format(FSLDIR),'-i', t1, '-u', '{}_all_{}_origsegs'.format(oname, btype),
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', '{}_all_{}_firstsegs'.format(oname, btype)]
        print('{}/bin/first_mult_bcorr'.format(FSLDIR),'-i', t1, '-u', '{}_all_{}_origsegs'.format(oname, btype),
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', '{}_all_{}_firstsegs'.format(oname, btype))
        check_call(cmd)

def get_t1(mse):
    t1_file = ""
    with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)

    return t1_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    print("mse is:", mse)
    t1 = get_t1(mse)
    odir = '{}/{}/first_all_BS/'.format(_get_output(mse),mse)
    print(odir)
    n4 = '{}/{}/N4corr/'.format(_get_output(mse),mse) + t1.split('/')[-1]
    if not os.path.exists('{}/{}/N4corr/'.format(_get_output(mse),mse)):
        os.mkdir('{}/{}/N4corr/'.format(_get_output(mse),mse))
        cmd = ["N4BiasFieldCorrection","-d", "3", "-i", t1, "-o",n4 ]
        Popen(cmd).wait()
    run_first(n4, odir)