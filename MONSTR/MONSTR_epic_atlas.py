import os
import argparse
import subprocess
from subprocess import check_call
from glob import glob
import pbr
from pbr.base import _get_output
import json



atlas = "/data/henry7/james/MONSTR/EPIC_Atlas/"
MONSTR = "/data/henry7/james/MONSTR/MONSTR.sh"


def get_scan(mse, file):
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

def nifti_convert(file):
    new_nifti = output +  file.split('/')[-1].replace('.gz','')
    print('mri_convert', file, new_nifti)
    check_call(['mri_convert', file, new_nifti])

def run_monstr(mse):
    t1 = get_scan(mse, 't1_files')
    t2 = get_scan(mse, 't2_files')
    flair = get_scan(mse, 'flair_files')
    print(t1)


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



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code runs MONSTR brain extraction using EPIC brain atlases as a reference')
    parser.add_argument('-mse', help = 'Input the mseID')
    parser.add_argument
    args = parser.parse_args()
    mse = args.mse
    output = _get_output(mse) +'/' + mse + '/MONSTR/'
    if not os.path.exists(output):
        os.mkdir(output)
    run_monstr(mse)