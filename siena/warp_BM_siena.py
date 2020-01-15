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

pbr_long ="/data/henry12/siena_BM/"

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
        cmd = ["sienax_optibet", get_t1(mse), "-r", "-d", "-o", _get_output(mse)+'/'+mse + '/sienaxorig_noles']
        check_call(cmd)
        bm =  _get_output(mse)+'/'+mse + '/sienaxorig_noles/I_brain_mask.nii.gz'
    return bm

"""def get_bm(tp_brain):
    bm = tp_brain.replace(".nii", "_optiBET_brain_mask.nii")
    print(bm)
    if not os.path.exists(bm):
        cmd = ["/netopt/share/bin/local/optiBET.sh", "-i", tp_brain]
        check_call(cmd)
    return bm"""


def make_wd(mse1, mse2):
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    if not os.path.exists(pbr_long + msid):
        os.mkdir(pbr_long + msid)
    warp_dir = pbr_long + msid + '/warp/'
    wd = '{0}/{1}_{2}/'.format(warp_dir, mse1, mse2)
    print("MSID:", msid)
    if not os.path.exists(warp_dir):
        print(warp_dir)
        os.mkdir(warp_dir)

    if not os.path.exists(wd):
         print(wd)
         os.mkdir(wd)
    return wd


def get_t1_mni(mse, t1_file):
    t1 = t1_file.split("/")[-1]
    bl_t1 = '{0}/{1}/alignment/baseline_mni/{2}'.format(_get_output(mse), mse, t1.replace(".nii", "_T1mni.nii"))
    return bl_t1


def run_warp( mse1, mse2, wd):
    tp1_brain = get_t1(mse1)
    tp2_brain = get_t1(mse2)
    tp1_affine_tp2space = '{0}/{1}_{2}_affine.nii.gz'.format(wd,mse1, mse2)
    tp1_warp_tp2space = '{0}/{1}_{2}_warp.nii.gz'.format(wd,mse1, mse2)
    inv_warp = '{0}/{1}_{2}_warp_field_inv.nii.gz'.format(wd,mse1, mse2)
    tp1_tp2_brain_mask = wd + mse1+"_BM_"+ mse2 + "space.nii.gz"
    combined_bm_tp2 =  wd + "combined_BM_{}space.nii.gz".format(mse2)
    tp1_bm = get_bm(mse1)
    tp2_bm = get_bm(mse2)
       
                                                             
    #shutil.copyfile(tp1_brain, wd + tp1_brain.split('/')[-1])
    #shutil.copyfile(tp2_brain, wd + tp2_brain.split('/')[-1])
    #tp1_brain = wd + tp1_brain.split('/')[-1]
    #tp2_brain = wd + tp2_brain.split('/')[-1]


    #tp1_brain = get_t1_mni(mse1, t1_file1)
    #tp2_brain = get_t1_mni(mse2, t1_file2)
    msid = get_t1(mse1).split('/')[-1].split('-')[0]
    warp_final = pbr_long + msid   + "/warp/"
    #if not os.path.exists(warp_final + mse1 + "_" +mse2 ):

    if not os.path.exists(tp1_affine_tp2space):
        cmd = ['flirt','-dof','6', '-in',tp1_brain, '-ref', tp2_brain, '-out', tp1_affine_tp2space,  "-omat",  wd + "affine.mat"]
        print('flirt', '-in',tp1_brain, '-ref', tp2_brain, '-out', tp1_affine_tp2space,  "-omat",  wd + "affine.mat")
        check_call(cmd)

    cmd = ["flirt", "-init", wd + "affine.mat" , "-applyxfm", "-in", tp1_bm, "-ref", tp2_brain, "-out", tp1_tp2_brain_mask]
    print("flirt", "-init", wd + "affine.mat" , "-applyxfm", "-in", tp1_bm, "-ref", tp2_brain, "-out", tp1_tp2_brain_mask)
    check_call(cmd)

    if not os.path.exists(tp1_warp_tp2space):
        cmd = ["fnirt", "--ref={}".format(tp2_brain), "--in={}".format(tp1_brain), "--cout={}".format(tp1_warp_tp2space), "--iout={}".format(tp1_warp_tp2space).replace(".nii", "_img.nii")] # "--aff={}".format(wd+ "affine.mat")
        print("fnirt", "--ref={}".format(tp2_brain), "--in={}".format(tp1_brain), "--cout={}".format(tp1_warp_tp2space),"--iout={}".format(tp1_warp_tp2space).replace(".nii", "_img.nii"))
        check_call(cmd)

    cmd = ["applywarp","-r", tp2_brain,"-i", tp1_bm,"-o",tp1_warp_tp2space.replace(".nii", "_new.nii"), "-w",tp1_warp_tp2space, "--premat={}".format(wd+ "/affine.mat")]
    print( "applywarp","-r", tp2_brain,"-i", tp1_bm,"-o",tp1_warp_tp2space.replace(".nii", "_new.nii"), "-w",tp1_warp_tp2space, "--premat={}".format(wd+ "affine.mat") )
    check_call(cmd)

    cmd = ["fslmaths", tp1_warp_tp2space.replace(".nii","_new.nii"), "-mul", tp2_bm, combined_bm_tp2]
    print("fslmaths", tp1_warp_tp2space.replace(".nii","_new.nii"), "-mul", tp2_bm, combined_bm_tp2)
    check_call(cmd)

    cmd = ["invwarp","-w", tp1_warp_tp2space,"-o", inv_warp,"-r",  tp1_affine_tp2space ]
    print("invwarp","-w", tp1_warp_tp2space,"-o", inv_warp,"-r",  tp1_affine_tp2space )
    check_call(cmd)

    cmd = ["applywarp","-i", combined_bm_tp2, "-r", tp1_affine_tp2space,"-o", wd + "combined_BM_{}_warpspace.nii.gz".format(mse1), "-w", inv_warp ]
    print("applywarp","-i", combined_bm_tp2, "-r", tp1_affine_tp2space,"-o", wd + "combined_BM_{}_warpspace.nii.gz".format(mse1), "-w", inv_warp)
    check_call(cmd)

    cmd = ["convert_xfm", "-inverse", wd + "affine.mat", "-omat", wd + "inv_aff.mat"]
    print("convert_xfm", "-inverse", wd + "affine.mat", "-omat", wd + "inv_aff.mat")
    check_call(cmd)

    cmd = ["flirt", "-in",wd + "combined_BM_{}_warpspace.nii.gz".format(mse1), "-ref", tp1_brain, "-applyxfm","-init", wd + "inv_aff.mat" , "-o", wd + "combined_BM_{}space.nii.gz".format(mse1) ]
    print("flirt", "-in",wd + "combined_BM_{}_warpspace.nii.gz".format(mse1), "-ref", tp1_brain, "-applyxfm","-init", wd + "inv_aff.mat" , "-o", wd + "combined_BM_{}space.nii.gz".format(mse1) )
    check_call(cmd)
    siena_final = pbr_long + msid   + "/siena_fnirtBM_fromBL/"
    if not os.path.exists(siena_final + mse1 + "_" +mse2 ):
        cmd =["/data/henry6/gina/scripts/siena_BMinput",get_t1(mse1), get_t1(mse2), "-bm1",\
              wd + "combined_BM_{}space.nii.gz".format(mse1),"-bm2", combined_bm_tp2, "-o", siena_final + mse1 + "_" +mse2 ]
        print("*************************************************************")
        print(cmd)
        check_call(cmd)



    




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
    run_warp(mse1, mse2, wd)
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
                try:
                    run_warp(mse1, mse2, wd)
                except:
                    pass"""




