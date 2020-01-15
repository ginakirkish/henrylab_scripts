import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import pandas as pd
from pbr.config import config
import shutil
import nibabel as nib
import nilearn
from nilearn import masking



def get_t1(mse):
    t1 = ""
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1


def reg_to_BL(mse_list, long, msid):
    bl_mse = mse_list[0]
    bl_t1 = get_t1(bl_mse)
    other_mse = mse_list[1:]
    for mse in other_mse:
        t1_in = get_t1(mse)
        jacobian_path = config["long_output_directory"] +"/"+msid + '/jacobian/'
        affine = jacobian_path + bl_mse + "_affinereg_" + mse + ".mat"
        affine_reg = jacobian_path + bl_mse + "_affinereg_" + mse + ".nii.gz"

        if not os.path.exists(affine_reg):
            cmd=['flirt','-ref',bl_t1,'-in',t1_in,'-omat',affine,'-out',affine_reg]
            Popen(cmd).wait()

        first = get_first(mse)
        wm = get_sienax(mse)[0]
        gm = get_sienax(mse)[1]
        csf = get_sienax(mse)[2]
        pGM = get_sienax(mse)[3]
        bm = get_sienax(mse)[4]
        lesion = get_sienax(mse)[5]

        brain_masks = [first, wm, gm, csf, pGM, bm, lesion]
        for mask in brain_masks:
            if not os.path.exists(mask):
                continue
            if mask == first:
                bl = get_first(bl_mse)
                seg = "first"
            elif mask == wm:
                bl = get_sienax(bl_mse)[0]
                seg = "wm"
            elif mask == gm:
                bl = get_sienax(bl_mse)[1]
                seg = "gm"
            elif mask == csf:
                bl = get_sienax(bl_mse)[2]
                seg = "csf"
            elif mask == pGM:
                bl = get_sienax(bl_mse)[3]
                seg = "pGM"
            elif mask == bm:
                bl = get_sienax(bl_mse)[4]
                seg = "bm"
            elif mask == lesion:
                bl = get_sienax(bl_mse)[5]
                seg = "les"
            else:
                bl = ""

            mask_out = '{}/{}/'.format(long, seg)
            print(mask_out)
            if not os.path.exists(mask_out):os.mkdir(mask_out)

            out_mse = mask_out +bl_mse+ "_affine_"+ mse + ".nii.gz"

            cmd = ["flirt","-init",affine, "-applyxfm", "-in", mask,"-ref", bl_t1, "-out", out_mse]
            Popen(cmd).wait()

            cmd = ["fslmaths", mask, "-bin", out_mse.replace(".n","-bin.n")]
            Popen(cmd).wait()


            cmd = ["fslmaths", bl,"-bin", mask_out+ bl_mse+"{}_seg-bin_BL".format(seg)]
            print("fslmaths", bl,"-bin", mask_out+ bl_mse+"{}_seg-bin_BL".format(seg))
            Popen(cmd).wait()

            shutil.copy(bl,mask_out+ bl_mse+ "-{}_segBL.nii.gz".format(seg))


def combine_masks(mse_long, long):
    brain_masks = ["first", "wm", "gm", "csf", "pGM", "bm", "lesion"]
    for mask in brain_masks:
        combined_mask ="{}/{}/combined-{}_mask.nii.gz".format(long, mask, mask)
    #num = len([name for name in os.listdir(long) if "first_seg-bin" in name])
    list = []
    mask_out = '{}/{}/'.format(long + str(mask))
    for segmentation in os.listdir(mask_out):
        if "seg-bin" in segmentation:
            list.append(mask_out+ segmentation)
    print(list)

    combined_image = nilearn.masking.intersect_masks(list, threshold=0.5, connected=True)
    combined_image.to_filename(mask_out + "combined_{}-bin.nii.gz".format(mask))
    if "first" in mask:

        cmd = ["fslmaths", get_first(mse_long[0]), "-dilM", "-mul", long+"/first/combined_first-bin.nii.gz", combined_mask.replace("-bin","")]
        Popen(cmd)
    return combined_mask

def mult_jacobia(long, first_mask):
    for files in os.listdir(long):
        if "jacobian" in files:
            mse = files.split("_ja")[0]
            cmd = ["fslmaths", long + files, "-mul", first_mask, long +'/first/'+ mse+ "jacobia_first.nii.gz"]
            Popen(cmd).wait()


def get_first(mse):
    first = ""
    first_seg = glob("{}/{}/first_all/*first*seg*.nii.gz".format(_get_output(mse),mse))
    if len(first_seg) == 0:
        cmd = ["pbr", mse, "-w", "first_all", "-R"]
        Popen(cmd).wait()
    else:
        print(mse, "EXISTS")
        first = first_seg[0]
    return first

def get_t2_les(mse):
    t2_les_path = glob("{}/{}/lesion_origspace*/lesion.nii.gz".format(_get_output(mse),mse))
    if len(t2_les_path)>0:
        t2_les = t2_les_path[0]
    else:
        t2_les = ""
    return t2_les

def get_sienax(mse):
    wm_path = glob("{}/{}/sienax_optibet/ms*/I_stdmaskbrain_seg_2.nii.gz".format(_get_output(mse),mse))
    wm_path2 = glob("{}/{}/sienaxorig_*/I_stdmaskbrain_seg_2.nii.gz".format(_get_output(mse),mse))
    if len(wm_path)>0:
        wm = wm_path[0]
    elif len(wm_path2)>0:
        wm = wm_path2[-1]
    else:
        wm = ""
    gm = wm.replace("seg_2", "seg_1")
    bm = wm.replace("I_stdmaskbrain_seg_2", "I_brain")
    pGM = wm.replace("I_stdmaskbrain_seg_2","I_stdmask_segperiph")
    csf = wm.replace("seg_2", "seg_0")
    lesion = wm.replace("I_stdmaskbrain_seg_2", "lesion_mask")
    return wm, gm, csf,pGM, bm, lesion

def get_mse(df):
    ms = "ms1757"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            mse_list.append(mse)
        else:
            ms = msid
            mse_list = []
        jacobian_path = config["long_output_directory"] +"/"+msid + "/jacobian/"
        long = jacobian_path + "/average_masks/"

        if not os.path.exists(config["long_output_directory"] +"/"+msid): os.mkdir(config["long_output_directory"] +"/"+msid)
        if not os.path.exists(jacobian_path):os.mkdir(jacobian_path)
        if not os.path.exists(long):os.mkdir(long)
        reg_to_BL(mse_list, long, msid)

    return mse_list, long, msid



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    dir = get_mse(df)
    first_mask = combine_masks(dir[0], dir[1])
    mult_jacobia(dir[1], first_mask)


