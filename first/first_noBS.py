
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
        for s in ['L_Accu', 'L_Amyg', 'L_Caud', 'L_Hipp', 'L_Puta', 'L_Thal', 'R_Accu', 'L_Pall',
                  'R_Amyg', 'R_Caud', 'R_Hipp', 'R_Pall', 'R_Puta', 'R_Thal']:

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
    odir = '{}/{}/first_all/'.format(_get_output(mse),mse)
    print(odir)
    run_first(t1, odir)

