__author__ = 'gkirkish'

import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import shutil
from subprocess import check_call
import subprocess


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
        for s in ['L_Accu', 'L_Amyg', 'L_Caud', 'L_Hipp', 'L_Puta', 'L_Thal', 'R_Accu', 'L_Pall',
                  'R_Amyg', 'R_Caud', 'R_Hipp', 'R_Pall', 'R_Puta', 'R_Thal', 'BrStem']:

            modelN = '336'
            bcorr = '1'
            intref = '0'
            if 'Accu' in s:
                nmodes = '50'
            elif 'Amyg' in s:
                nmodes = '50'
                intref = '1'
            elif 'Caud' in s:
                nmodes = '30'
                intref= '1'
            elif 'Hipp' in s:
                nmodes = '30'
                intref = '1'
            elif 'Late' in s:
                nmodes = '40'
                intref = '1'
            elif 'Pall' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'Puta' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'Thal' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'BrStem' in s:
                nmodes = '40'
                #bcorr = '0'
            else:
                raise ValueError('The structure {} is not in the structure list'.format(s))


            imfirst = '{}-{}_first'.format(oname, s)
            imsfirst.append(imfirst)

            FSLDIR = '/netopt/fsl5'

            if intref == '0':
                if bcorr == '1':
                    cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                           '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/{}_bin.bmv'.format(FSLDIR, modelN, s)]
                else:
                     cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                           '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/05mm/{}_05mm.bmv'.format(FSLDIR, modelN, s)]
            else:
                cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                       '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/intref_thal/{}.bmv'.format(FSLDIR, modelN, s), '-intref', '{}/data/first/models_{}_bin/05mm/{}_Thal_05mm.bmv'.format(FSLDIR, modelN, s.split('_')[0])]
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
        first_seg = '{}_all_{}_firstsegs'.format(oname, btype)

        cmd = ['{}/bin/fslmerge'.format(FSLDIR), '-t', first_seg]


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
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', first_seg]
        print('{}/bin/first_mult_bcorr'.format(FSLDIR),'-i', t1, '-u', '{}_all_{}_origsegs'.format(oname, btype),
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', first_seg)
        check_call(cmd)
        t1 = get_t1(mse)
        orig_fov(mse, t1, first_seg)
        create_json(first_seg)


def get_t1(mse):
    t1_file = ""
    with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)

    return t1_file

def run_n4(mse,t1):
    n4 = '{}/{}/N4corr/'.format(_get_output(mse),mse) + t1.split('/')[-1]

    if not os.path.exists('{}/{}/N4corr/'.format(_get_output(mse),mse)):
        os.mkdir('{}/{}/N4corr/'.format(_get_output(mse),mse))
    cmd = ["N4BiasFieldCorrection","-d", "3", "-i", t1, "-o",n4 ]
    Popen(cmd).wait()

def get_dim(t1):
    cmd = ["fslhd", t1]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    dim1, dim2, dim3 = "","",""
    for l in output:
        if "dim1" in l:
            dim1 = l[-1]
        if "dim2" in l:
            dim2 = l[-1]
        if "dim3" in l:
            dim3 = l[-1]
    print(dim3)
    return [dim1, dim2, dim3]

def orig_fov(mse, t1, first_seg):
    dim = get_dim(t1)
    dim1 = dim[0]
    dim2 = dim[1]
    dim3 = dim[2]
    print(dim1, dim2, dim3)
    first_seg_dim = first_seg.replace(".nii","_origdim.nii")
    new_z = 182 - int(dim3)
    cmd = ["fslroi", first_seg, first_seg_dim, '0', dim1, '0',dim2, str(new_z), dim3 ]
    print("***********",cmd)
    Popen(cmd).wait()

def fix_fov(mse,t1):
    dim = get_dim(t1)
    dim1 = dim[0]
    dim2 = dim[1]
    dim3 = dim[2]
    BS_dir = "{}/{}/first_new/".format(_get_output(mse), mse)
    if not os.path.exists(BS_dir):
        os.mkdir(BS_dir)
    new_dim_t1 = BS_dir + t1.split('/')[-1]
    print(new_dim_t1)
    new_z =  int(dim3) - 182
    print("#########", new_z)
    cmd = ["fslroi", t1, new_dim_t1, '0', dim1, '0',dim2, str(new_z), '182']
    print(cmd)
    Popen(cmd).wait()

    n4 = new_dim_t1.replace(".nii", "_N4.nii")
    cmd = ["N4BiasFieldCorrection","-d", "3", "-i", new_dim_t1, "-o",n4 ]
    Popen(cmd).wait()
    return n4



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    print("mse is:", mse)
    t1 = get_t1(mse)
    print(t1)
    t1_fixed = fix_fov(mse,t1)

    odir = '{}/{}/first_new/'.format(_get_output(mse),mse)
    print(odir)
    run_first(t1_fixed, odir)