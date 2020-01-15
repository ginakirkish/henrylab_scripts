from subprocess import check_call
from time import time
import argparse
import json
import pbr
from pbr.base import _get_output
from glob import glob
import os
import shutil

nrigid_path = "/data/henry6/gina/henrylab_utils/nrigid/"
pbr_long = "/data/henry10/PBR_long/subjects/"


def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file

def get_bm(mse):
    BM = glob('{0}/{1}/sienaxorig_*/I_brain_mask.nii.gz'.format(_get_output(mse), mse))
    if BM:
        bm = BM[0]
    else:
        bm = ""
    return bm


def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    w_nrigid = pbr_long + msid + '/nrigid/'
    wd = '{0}/{1}_{2}/'.format(w_nrigid, mse1, mse2)
    print("MSID:", msid)
    if not os.path.exists(w_nrigid):
        print(w_nrigid)
        os.mkdir(w_nrigid)

    if not os.path.exists(wd):
         print(wd)
         os.mkdir(wd)
    return wd


def run_rigid( mse1, mse2, wd):

    output_affine = '{0}/{1}_{2}_affine.nii.gz'.format(make_wd(mse1, mse2),mse1, mse2)
    cmd = ['flirt', '-in', get_t1(mse1), '-ref', get_t1(mse2), '-out', output_affine, '-omat', wd + "affine.mat"]
    print(cmd)
    check_call(cmd)

    cmd = ["flirt", "-init", wd + "affine.mat" , "-applyxfm", "-in", get_bm(mse1), "-ref", get_t1(mse2), "-out", wd + mse1+"_BM_"+ mse2 + "space.nii.gz" ]
    print(cmd)
    check_call(cmd)

    cmd = ["mri_convert", wd + mse1+"_BM_"+ mse2 + "space.nii.gz",  wd + mse1+"_BM_"+ mse2 + "space.img"  ]
    check_call(cmd)


def convert_nii2hdr(mse1, mse2):
    output_flirt = '{0}/{1}_{2}_flirt.nii.gz'.format(make_wd(mse1, mse2),mse1, mse2)
    output_affine = '{0}/{1}_{2}_affine.nii.gz'.format(make_wd(mse1, mse2),mse1, mse2)

    # convert the moving image
    output_affine_hdr = output_affine.split('.nii')[0] + '.img'
    cmd = ['mri_convert', output_affine, output_affine_hdr]
    print(cmd)
    check_call(cmd)

    # convert the fixed image
    fixed_img_hdr = '/'.join(output_flirt.split('/')[:-1]) + '/' +  get_t1(mse2).split('/')[-1].split('.nii.gz')[0] +'.img'
    cmd = ['mri_convert', get_t1(mse2), fixed_img_hdr]
    print(cmd)
    check_call(cmd)


def run_nrigid(mse1, mse2):
    outroot = make_wd(mse1, mse2) + '{0}_{1}_nrigid'.format(mse1, mse2)
    output_affine_hdr = '{0}/{1}_{2}_affine.hdr'.format(make_wd(mse1, mse2),mse1, mse2)
    output_flirt = '{0}/{1}_{2}_flirt.nii.gz'.format(make_wd(mse1, mse2),mse1, mse2)
    fixed_img_hdr = '/'.join(output_flirt.split('/')[:-1]) + '/' +  get_t1(mse2).split('/')[-1].split('.nii.gz')[0] +'.hdr'
    cmd = ['{0}/msNrigid'.format(nrigid_path), output_affine_hdr,fixed_img_hdr, outroot]
    start = time()
    print(cmd)
    check_call(cmd)
    print('Took {} seconds to run'.format(time()-start))

def convertimg2hdr(mse1, mse2):
    outroot = make_wd(mse1, mse2) + '{0}_{1}_nrigid_def.img'.format(mse1, mse2)
    cmd = ['mri_convert', outroot, outroot.replace(".img", ".nii.gz")]
    print(cmd)
    check_call(cmd)


def apply_nrigid_to_mask(mse1, mse2):
    bm_ref = make_wd(mse1, mse2) + "{0}_BM_reference".format(mse2)
    transform_field = make_wd(mse1, mse2) + '{0}_{1}_nrigid_field.hdr'.format(mse1, mse2)
    new_BM =  make_wd(mse1, mse2)+'{0}_{1}_nrigid_bm.hdr'.format(mse1, mse2)

    cmd = ["mri_convert", get_bm(mse2), bm_ref + ".img"]
    print(cmd)
    check_call(cmd)

    cmd = [nrigid_path + "msDeform", "-m", transform_field, wd + mse1+"_BM_"+ mse2 + "space.hdr", new_BM ]
    print(cmd)
    check_call(cmd)

    cmd = ["mri_convert", new_BM.replace(".hdr", ".img"), new_BM.replace(".hdr", ".nii.gz")]
    print(cmd)
    check_call(cmd)

def combine_BM(mse1, mse2):
    new_BM = make_wd(mse1, mse2)+'{0}_{1}_nrigid_bm.nii.gz'.format(mse1, mse2)
    combined_bm = make_wd(mse1, mse2) + "{0}_BM_combined.nii.gz".format(mse2)
    cmd = ["fslmaths", new_BM.replace("bm", "BM"), "-mul",  get_bm(mse2), combined_bm]
    print(cmd)
    check_call(cmd)


def transform_ref_back(mse1, mse2):
    combined_bm = make_wd(mse1, mse2) + "{0}_BM_combined.nii.gz".format(mse2)
    output_affine_hdr = '{0}/{1}_{2}_affine.hdr'.format(make_wd(mse1, mse2),mse1, mse2)
    transform_field = make_wd(mse1, mse2) + '{0}_{1}_nrigid_field.hdr'.format(mse1, mse2)

    #cmd =[nrigid_path + "msInvertDef", transform_field, output_affine_hdr ,make_wd(mse1, mse2) + "inverse_combined.hdr"]
    cmd = [nrigid_path + "msInvertDef", transform_field, get_t1(mse2),make_wd(mse1, mse2) + "inverse_combined.hdr"]
    print(cmd)
    check_call(cmd)

    cmd = ["mri_convert", combined_bm, combined_bm.replace(".nii.gz", ".img")]
    check_call(cmd)

    cmd = [nrigid_path + "msDeform", "-e", "-m", make_wd(mse1, mse2)+"inverse_combined.hdr", combined_bm.replace(".nii.gz", ".hdr") ,make_wd(mse1, mse2) + "final_combined_bm_tp1tp2space.hdr" ]
    print(cmd)
    check_call(cmd)

    cmd = ["mri_convert", make_wd(mse1, mse2) + "final_combined_bm_tp1tp2space.img", make_wd(mse1, mse2) + "final_inverse_combined.nii.gz"]
    print(cmd)
    check_call(cmd)

    print("*******************")
    print(get_t1(mse1), make_wd(mse1, mse2)+ "final_inverse_combined.nii.gz")
    print(get_t1(mse2), combined_bm)
    print("***************")


def run_all(mse1,mse2, wd):
    run_rigid(mse1, mse2, wd)
    convert_nii2hdr(mse1, mse2)
    run_nrigid(mse1,mse2)
    convertimg2hdr(mse1, mse2)
    apply_nrigid_to_mask(mse1, mse2)
    combine_BM(mse1, mse2)
    transform_ref_back(mse1, mse2)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-mse1', help = 'MSE1 - Moving subject')
    parser.add_argument('-mse2', help = 'MSE2 - Reference Subject')
    args = parser.parse_args()
    mse1 = args.mse1
    mse2 = args.mse2
    wd = make_wd(mse1, mse2)
    mse1_t1 = get_t1(mse1)
    mse2_t1 = get_t1(mse2)
    print(wd)
    #out = args.o
    run_all(mse1, mse2, wd)