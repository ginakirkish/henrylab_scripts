import os
import argparse
import subprocess
from subprocess import check_call
from glob import glob
import pbr
from pbr.base import _get_output
import json
import pandas as pd



atlas = "/data/henry7/james/MONSTR/EPIC_Atlas/"
MONSTR = "/data/henry7/james/MONSTR/MONSTR.sh"
pbr_long = "/data/henry12/siena_BM/"


def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file

def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    if not os.path.exists(pbr_long + msid):
        os.mkdir(pbr_long + msid)
    w_nrigid = pbr_long + msid + '/MONSTRsiena/'
    wd = '{0}/{1}_{2}/'.format(w_nrigid, mse1, mse2)
    print("MSID:", msid)
    if not os.path.exists(w_nrigid):
        print(w_nrigid)
        os.mkdir(w_nrigid)

    if not os.path.exists(wd):
         print(wd)
         os.mkdir(wd)
    return wd



def get_scan(mse, file, output):
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data[file]) > 0:
                file = data[file][-1].replace("_reorient","")
                print(file)
                new_nifti = output +  file.split('/')[-1].replace('.gz','')
                print('mri_convert', file, new_nifti)
                check_call(['mri_convert', file, new_nifti])
            else:
                new_nifti = ""
            return new_nifti


def rotate_BM(mse, output, t1):
    try:
        smooth_BM = glob(output + "/ms*/t1_MultiModalStripMask_smooth.nii.gz")[0]
        final_MONSTR = t1.split('.nii.gz','_MONSTR_brain_mask.nii.gz')
        cmd = ['fslreorient2std', smooth_BM, final_MONSTR]
        check_call(cmd)
        print(cmd)
        cmd = ['fslmaths', t1, '-mul', final_MONSTR, final_MONSTR.replace('_mask','')]
        check_call(cmd)
        print(cmd)
    except:
        pass
    try:
        BM = glob(output + "/ms*/t1_MultiModalStripMask.nii.gz")[0]
        cmd = ['fslreorient2std', BM, output + '/'+mse +'_brain_mask.nii.gz']
        check_call(cmd)
        print(cmd)

    except:
        pass

"""def nifti_convert(file, output):
    new_nifti = output +  file.split('/')[-1].replace('.gz','')
    print('mri_convert', file, new_nifti)
    check_call(['mri_convert', file, new_nifti])"""

def run_monstr(mse, output):
    t1 = get_scan(mse, 't1_files', output)
    t2 = get_scan(mse, 't2_files', output)
    flair = get_scan(mse, 'flair_files', output)
    print(t1)
    try:

        if len(t1) > 1 and len(t2) > 1 and len(flair) > 1:
            cmd = [MONSTR, '--t1', t1,'--t2',t2,'--fl', flair,'--atlasdir',atlas, '--robust', 'ncpu', '4','NumAtlas','6', '--o', output]
            print(cmd)
            check_call(cmd)
        elif len(t1) > 1 and len(t2) > 1:
            cmd = [MONSTR, '--t1', t1,'--t2',t2,'--atlasdir',atlas, '--robust', 'ncpu', '4','NumAtlas','6', '--o', output]
            print(cmd)
            check_call(cmd)
        elif len(t1) > 1 and len(flair) > 1:
            cmd = [MONSTR, '--t1', t1,'--fl',flair,'--atlasdir',atlas, '--robust', 'ncpu', '4','NumAtlas','6', '--o', output]
            print(cmd)
            check_call(cmd)
        elif len(t1) > 1:
            cmd = [MONSTR, '--t1', t1,'--atlasdir',atlas, '--robust', 'ncpu', '4','NumAtlas','6', '--o', output]
            print(cmd)
            check_call(cmd)
        else:
            print("{0} NO T1 image to perform brain extraction".format(mse))
        rotate_BM(mse, output, t1)
    except:
        pass


def run_siena(mse1, mse2, output1, output2):

    msid = get_t1(mse1).split('/')[-1].split('-')[0]

    cmd =["/data/henry6/gina/scripts/siena_BMinput",get_t1(mse1), get_t1(mse2), "-bm1",output1 + '/'+mse1 +'_brain_mask.nii.gz' ,\
          "-bm2",output2 + '/'+mse2 +'_brain_mask.nii.gz' , "-o", pbr_long + msid + '/siena_MONSTR/'+mse1 + "_" +mse2 ]

    check_call(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-mse1', help = 'MSE1 - Moving subject')
    parser.add_argument('-mse2', help = 'MSE2 - Reference Subject')
    args = parser.parse_args()
    mse1 = args.mse1
    mse2 = args.mse2
    output1 = _get_output(mse1) +'/' + mse1 + '/MONSTR/'
    if not os.path.exists(output1):
        os.mkdir(output1)
    output2 = _get_output(mse2) + '/' + mse2 + '/MONSTR/'
    if not os.path.exists(output2):
        os.mkdir(output2)
    mse1_t1 = get_t1(mse1)
    mse2_t1 = get_t1(mse2)
    if not os.path.exists(output1 + get_t1(mse1).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
        run_monstr(mse1, output1)
    if not os.path.exists(output2 + get_t1(mse2).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
        run_monstr(mse2, output2)
    msid = get_t1(mse1).split('/')[-1].split("-")[0]
    if not os.path.exists('/data/henry12/siena_BM/'+ msid + '/siena_MONSTR/'+mse1 + "_" +mse2 + '/report.html'):
        run_siena(mse1, mse2, output1, output2)


    """parser = argparse.ArgumentParser()
    parser.add_argument('-mse1', help = 'MSE1 - Moving subject')
    parser.add_argument('-mse2', help = 'MSE2 - Reference Subject')
    args = parser.parse_args()
    mse1 = args.mse1
    mse2 = args.mse2
    output1 = _get_output(mse1) +'/' + mse1 + '/MONSTR/'
    if not os.path.exists(output1):
        os.mkdir(output1)
    output2 = _get_output(mse2) + '/' + mse2 + '/MONSTR/'
    if not os.path.exists(output2):
        os.mkdir(output2)
    mse1_t1 = get_t1(mse1)
    mse2_t1 = get_t1(mse2)
    if not os.path.exists(output1 + get_t1(mse1).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
        run_monstr(mse1, output1)
    if not os.path.exists(output2 + get_t1(mse2).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
        run_monstr(mse2, output2)
    msid = get_t1(mse1).split('/')[-1].split("-")[0]
    if not os.path.exists('/data/henry12/siena_BM/'+ msid + '/siena_MONSTR/'+mse1 + "_" +mse2 + '/report.html'):
        run_siena(mse1, mse2, output1, output2)

    #run_monstr(mse1, output1)
    #run_monstr(mse2, output2)
    #run_siena(mse1, mse2, output1, output2)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    ind = 0
    baseline_msid, mse_baseline, mse2 = ["","",""]
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx,'mse']

        if msid == baseline_msid:
            x = 0
            ind = ind+1
            #print(ind, msid, mse)
        else:
            baseline_msid = msid
            ind = 0
        if ind == 0 :
            mse1 =  df.loc[idx,'mse']
        if not mse1 == mse:
            mse2 = mse
            print(mse1, mse)
            wd = make_wd(mse1, mse2)
            output1 = _get_output(mse1) +'/' + mse1 + '/MONSTR/'
            if not os.path.exists(output1):
                os.mkdir(output1)
            output2 = _get_output(mse2) + '/' + mse2 + '/MONSTR/'
            if not os.path.exists(output2):
                os.mkdir(output2)

            if not os.path.exists(output1 + get_t1(mse1).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
                run_monstr(mse1, output1)
            if not os.path.exists(output2 + get_t1(mse2).split('/')[-1].split('.nii.gz')[0] + "_MultiModalStripMask.nii"):
                run_monstr(mse2, output2)
            if not os.path.exists('/data/henry12/siena_BM/MONSTR_siena/'+ msid + '/siena_MONSTR/'+mse1 + "_" +mse2 + '/report.html'):
                run_siena(mse1, mse2, output1, output2)"""


