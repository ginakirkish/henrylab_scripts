from subprocess import check_call
from time import time
import argparse
import json
import pbr
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd

nrigid_path = "/data/henry6/gina/henrylab_utils/nrigid/"
#pbr_long = "/data/henry10/PBR_long/subjects/"
pbr_long ="/data/henry6/gina/nrigid/"

def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file

"""def get_bm(mse):
    BM = glob('{0}/{1}/sienaxorig_*/I_brain_mask.nii.gz'.format(_get_output(mse), mse))
    if BM:
        bm = BM[0]
    else:
        bm = ""
    return bm"""
def get_bm(mse):
    BM =glob('{0}/{1}/sienax*/{2}/I_brain_mask.nii.gz'.format(_get_output(mse), mse, get_t1(mse).split('/')[-1].replace('.nii.gz','')))
    print(BM)
    if BM:
        bm = BM[-1]
    else:
        bm = ""
    return bm



def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    if not os.path.exists(pbr_long + msid):
        os.mkdir(pbr_long + msid)
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


def run_nrigid( mse1, mse2, wd):
    tp1_brain = get_t1(mse1)
    tp2_brain = get_t1(mse2)
    tp1_affine_tp2space = '{0}/{1}_{2}_affine.nii.gz'.format(wd,mse1, mse2)
    tp1_affine_tp2space_hdr = tp1_affine_tp2space.replace(".nii.gz", ".hdr")
    tp1_tp2space_nrigid =   wd + '{0}_{1}_nrigid'.format(mse1, mse2)
    nrigid_field = wd + '{0}_{1}_nrigid_field.hdr'.format(mse1, mse2)
    nrigid_def =   wd + '{0}_{1}_nrigid_def.img'.format(mse1, mse2)
    tp1_tp2_brain_mask = wd + mse1+"_BM_"+ mse2 + "space.nii.gz"
    tp1_tp2space_nrigid_bm =  wd+'{0}_{1}_nrigid_bm.hdr'.format(mse1, mse2)
    tp2_bm = get_bm(mse2)
    combined_bm_tp2 =  wd + "combined_BM_{}space.nii.gz".format(mse2)
    combined_bm_tp1tp2space = wd + "combined_bm_tp1tp2space.hdr"
    invert_def =    wd + "inverse_combined.hdr"
    tp2_brain_hdr = wd+ '/' +  tp2_brain.split('/')[-1].split('.nii.gz')[0] +'.hdr'

    cmd = ['flirt', '-in',tp1_brain, '-ref', tp2_brain, '-out', tp1_affine_tp2space,  "-omat",  wd + "affine.mat"]
    print('flirt', '-in',tp1_brain, '-ref', tp2_brain, '-out', tp1_affine_tp2space,  "-omat",  wd + "affine.mat")
    check_call(cmd)

    cmd = ["flirt", "-init", wd + "affine.mat" , "-applyxfm", "-in", get_bm(mse1), "-ref", tp2_brain, "-out", tp1_tp2_brain_mask]
    print("flirt", "-init", wd + "affine.mat" , "-applyxfm", "-in", get_bm(mse1), "-ref", tp2_brain, "-out", tp1_tp2_brain_mask)
    check_call(cmd)

    cmd = ["mri_convert", tp1_tp2_brain_mask,  tp1_tp2_brain_mask.replace(".nii.gz",".img") ]
    print("mri_convert", tp1_tp2_brain_mask,  tp1_tp2_brain_mask.replace(".nii.gz",".img"))
    check_call(cmd)

    # convert the moving image
    cmd = ['mri_convert', tp1_affine_tp2space, tp1_affine_tp2space_hdr.replace(".hdr",".img")]
    print('mri_convert', tp1_affine_tp2space, tp1_affine_tp2space_hdr.replace(".hdr",".img"))
    check_call(cmd)

    # convert the fixed image
    cmd = ['mri_convert', tp2_brain, tp2_brain_hdr.replace(".hdr",".img")]
    print('mri_convert', tp2_brain, tp2_brain_hdr.replace(".hdr",".img"))
    check_call(cmd)

    cmd = ['{0}/msNrigid'.format(nrigid_path), tp1_affine_tp2space_hdr, tp1_affine_tp2space_hdr,tp2_brain_hdr, tp1_tp2space_nrigid]
    start = time()
    print('{0}/msNrigid'.format(nrigid_path), tp1_affine_tp2space_hdr, tp1_affine_tp2space_hdr,tp2_brain_hdr, tp1_tp2space_nrigid)
    check_call(cmd)
    #print('Took {} seconds to run'.format(time()-start))

    cmd = [nrigid_path + "msDeform", "-m", nrigid_field, tp1_tp2_brain_mask.replace(".nii.gz",".hdr"), tp1_tp2space_nrigid_bm ]
    print(nrigid_path + "msDeform", "-m", nrigid_field, tp1_tp2_brain_mask.replace(".nii.gz",".hdr"), tp1_tp2space_nrigid_bm )
    check_call(cmd)

    cmd = ["mri_convert", tp1_tp2space_nrigid_bm.replace(".hdr", ".img"), tp1_tp2space_nrigid_bm.replace(".hdr", "_new.nii.gz")]
    print("mri_convert", tp1_tp2space_nrigid_bm.replace(".hdr", ".img"), tp1_tp2space_nrigid_bm.replace(".hdr", "_new.nii.gz"))
    check_call(cmd)

    cmd = ["fslcpgeom",tp2_bm, tp1_tp2space_nrigid_bm.replace(".hdr", "_new.nii.gz") ]
    check_call(cmd)

    cmd = ["fslmaths", tp1_tp2space_nrigid_bm.replace(".hdr", "_new.nii.gz"), "-mul",  tp2_bm, combined_bm_tp2]
    print("fslmaths", tp1_tp2space_nrigid_bm.replace(".hdr", "_new.nii.gz"), "-mul",  tp2_bm, combined_bm_tp2)
    check_call(cmd)

    cmd = [nrigid_path + "msInvertDef", nrigid_field, tp1_affine_tp2space.replace(".nii.gz",".hdr"),invert_def]
    print(nrigid_path + "msInvertDef", nrigid_field, tp1_affine_tp2space.replace(".nii.gz",".hdr"),invert_def)
    check_call(cmd)

    cmd = ["mri_convert", combined_bm_tp2, combined_bm_tp2.replace(".nii.gz", ".img")]
    print("mri_convert", combined_bm_tp2, combined_bm_tp2.replace(".nii.gz", ".img"))
    check_call(cmd)

    cmd = [nrigid_path + "msDeform", "-e", "-m", invert_def, combined_bm_tp2.replace(".nii.gz", ".hdr") , combined_bm_tp1tp2space]
    print(nrigid_path + "msDeform", "-e", "-m", invert_def, combined_bm_tp2.replace(".nii.gz", ".hdr") , combined_bm_tp1tp2space)
    check_call(cmd)

    cmd = ["mri_convert", combined_bm_tp1tp2space.replace(".hdr", ".img"), combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz")]
    print("mri_convert", combined_bm_tp1tp2space.replace(".hdr", ".img"), combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz"))
    check_call(cmd)

    print("fslhd", combined_bm_tp1tp2space)
    print("fslhd", tp1_brain)
    check_call("fslhd", combined_bm_tp1tp2space)
    check_call("fslhd", tp1_brain)

    print("fslcpgeom", tp1_brain, combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz"))
    cmd = ["fslcpgeom", tp1_brain, combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz")]
    check_call(cmd)

    print("fslhd",  combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz") )
    print("fslhd", tp1_brain)


    print("convert_xfm", "-inverse", wd + "affine.mat", "-omat", wd + "inverse_affine.mat")
    cmd = ["convert_xfm", "-inverse", wd + "affine.mat", "-omat", wd + "inverse_affine.mat"]
    check_call(cmd)


    print("flirt", "-in", combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz"), "-ref",get_t1(mse1), "-init", wd +"inverse_affine.mat", "-applyxfm", "-out", wd + "combined_BM_{}space.nii.gz".format(mse1))
    cmd = ["flirt", "-in", combined_bm_tp1tp2space.replace(".hdr", "_new.nii.gz"), "-ref",get_t1(mse1), "-init", wd +"inverse_affine.mat", "-applyxfm", "-out", wd + "combined_BM_{}space.nii.gz".format(mse1)]
    check_call(cmd)

    tp1_brain = get_t1(mse1)
    tp2_brain = get_t1(mse2)
    tp1_affine_tp2space = '{0}/{1}_{2}_affine.nii.gz'.format(wd,mse1, mse2)
    tp1_affine_tp2space_hdr = tp1_affine_tp2space.replace(".nii.gz", ".hdr")
    tp1_tp2space_nrigid =   wd + '{0}_{1}_nrigid'.format(mse1, mse2)
    nrigid_field = wd + '{0}_{1}_nrigid_field.hdr'.format(mse1, mse2)
    nrigid_def =   wd + '{0}_{1}_nrigid_def.img'.format(mse1, mse2)
    tp1_tp2_brain_mask = wd + mse1+"_BM_"+ mse2 + "space.nii.gz"
    tp1_tp2space_nrigid_bm =  wd+'{0}_{1}_nrigid_bm.hdr'.format(mse1, mse2)
    tp2_bm = get_bm(mse2)
    combined_bm_tp2 =  wd + "combined_BM_{}space.nii.gz".format(mse2)
    combined_bm_tp1tp2space = wd + "combined_bm_tp1tp2space.hdr"
    invert_def =    wd + "inverse_combined.hdr"
    tp2_brain_hdr = wd+ '/' +  tp2_brain.split('/')[-1].split('.nii.gz')[0] +'.hdr'

    os.remove(tp1_brain)
    os.remove(tp2_brain)
    os.remove(tp1_affine_tp2space)
    os.remove(nrigid_field)
    os.remove(tp1_tp2space_nrigid)
    os.remove(nrigid_def)
    os.remove(tp1_tp2_brain_mask)
    os.remove(tp2_bm)
    os.remove(combined_bm_tp2)
    os.remove(combined_bm_tp1tp2space)
    os.remove(invert_def)
    os.remove(tp2_brain_hdr)

    """msid = get_t1(mse1).split('/')[-1].split('-')[0]
    siena_final = pbr_long + msid  + "/siena_NrigidBM_fromBL/"
    print("************************************************************")
    cmd =["/data/henry6/gina/scripts/siena_BMinput",get_t1(mse1), get_t1(mse2), "-bm1",bm_tp1_final ,"-bm2", bm_tp2_final, "-o", siena_final + mse1 + "_" +mse2 ]
    print("*************************************************************")
    print(cmd)
    check_call(cmd)"""

if __name__ == '__main__':
    """parser = argparse.ArgumentParser()
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
    run_nrigid(mse1, mse2, wd)
    """
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
            if not os.path.exists(wd + 'A_halfwayto_B_render.png'):
                print("working directory", wd, mse1, mse2)
                #run_nrigid(mse1, mse2, wd)