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

def get_first(mse):
    first = ""
    first_seg = glob("{}/{}/first_all/*first*seg*.nii.gz".format(_get_output(mse),mse))
    if len(first_seg) == 0:
        cmd = ["pbr", mse, "-w", "first_all", "-R"]
        #Popen(cmd).wait()
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
        cmd = ["pbr", mse, "-w", "sienax_optibet","-R"]
        #Popen(cmd).wait()
    gm = wm.replace("seg_2", "seg_1")
    bm = wm.replace("I_stdmaskbrain_seg_2", "I_brain")
    pGM = wm.replace("seg_2","pve_1_segperiph")
    csf = wm.replace("seg_2", "seg_0")
    lesion = wm.replace("I_stdmaskbrain_seg_2", "lesion_mask")
    return wm, gm, csf,pGM, bm, lesion

def reg_to_BL(mse_list, msid, jacobian_dir, reg_to_bl, combined_masks):
    #defining baseline mse and non-baseline mse's
    bl_mse = mse_list[0]
    bl_t1 = get_t1(bl_mse)
    other_mse = mse_list[1:]
    for mse in other_mse:
        t1_in = get_t1(mse)
        if not os.path.exists(jacobian_dir):os.mkdir(jacobian_dir)
        if not os.path.exists(reg_to_bl):os.mkdir(reg_to_bl)

        # defining output files - all in folder /data/henry10/PBR_long/subjects/<msid>/jacobian/reg_to_baseline
        affine = reg_to_bl + mse + "_affinereg_" + bl_mse + ".mat"
        affine_reg = reg_to_bl + mse + "_affinereg_" + bl_mse + ".nii.gz"
        fnirt_reg = reg_to_bl + mse + "_fnirt_" + bl_mse + ".nii.gz"
        jacobian = reg_to_bl + mse + "_jacobian_" + bl_mse + ".nii.gz"


        #fllirt registration, t1's to baseline t1
        if not os.path.exists(affine_reg):
            cmd=['flirt','-ref',bl_t1,'-in',t1_in,'-omat',affine,'-out',affine_reg]
            Popen(cmd).wait()
        #fnirt registration, t1 to baseline t1, outputing the jacobian
        if not os.path.exists(fnirt_reg):
            cmd=['fnirt','--ref='+bl_t1,'--in='+t1_in,'--aff='+affine,'--iout='+fnirt_reg,'--jout='+jacobian]
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print("python /data/henry6/gina/scripts/grid_submit.py ", "'{} {} {} {} {} {}'".format('fnirt','--ref='+bl_t1,'--in='+t1_in,'--aff='+affine,'--iout='+fnirt_reg,'--jout='+jacobian))
            #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py","'","{}".format('fnirt'),"{}".format('--ref='+bl_t1), "{}".format('--in='+t1_in),"{}".format('--aff='+affine),"{}".format('--iout='+fnirt_reg),"{}".format('--jout='+jacobian)]
            print(cmd)
            Popen(cmd).wait()
            mse_jacobian = "{}/{}/jacobian/".format(_get_output(mse),mse)
            #sym link jacobian to subjects specific folder
            if not os.path.exists(mse_jacobian):os.mkdir(mse_jacobian)
            try:
                os.symlink(fnirt_reg, mse_jacobian + mse + "_fnirt_" + bl_mse + ".nii.gz")
                os.symlink(jacobian, mse_jacobian+mse + "_jacobian_" + bl_mse + ".nii.gz")
            except:
                pass

        #retrieving various masks
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

            if not os.path.exists(combined_masks):os.mkdir(combined_masks)

            mask_out = '{}/{}_'.format(combined_masks, seg)
            print(mask_out)

            out_mse = mask_out +mse+ "_affine_"+ bl_mse + ".nii.gz"


            # apply affine matrix to masks to get masks in baseline space
            cmd = ["flirt","-init",affine, "-applyxfm", "-in", mask,"-ref", bl_t1, "-out", out_mse]
            Popen(cmd).wait()

            #binarize masks
            cmd = ["fslmaths", mask, "-bin", out_mse.replace(".n","-bin.n")]
            Popen(cmd).wait()

            # binarize baseline mask and copy over to combined masks folder
            cmd = ["fslmaths", bl,"-bin", mask_out+ bl_mse+"_seg-bin_BL.nii.gz"]
            print("fslmaths", bl,"-bin", mask_out+ bl_mse+"_seg-bin_BL.nii.gz")
            Popen(cmd).wait()
            print("**************")

            shutil.copy(bl,mask_out+ bl_mse+ "-_segBL.nii.gz".format(seg))



def combine_masks(mse_long, combined_masks):
    first_combined = ""
    brain_masks = ["first", "wm", "gm", "csf", "pGM", "bm", "lesion"]
    for mask in brain_masks:
        list = []
        # check combined mask folder for masks that have been registered and binarized to the baseline space
        if not os.path.exists(combined_masks): os.mkdir(combined_masks)
        for segmentation in os.listdir(combined_masks):
            if "seg-bin" in segmentation and mask in segmentation:
                list.append(combined_masks+ segmentation)
        if len(list)>0:
            #use nilearn intersect mask function to find average masks in baseline space
            try:
                combined_image = nilearn.masking.intersect_masks(list, threshold=0.5, connected=True)
                combined_image.to_filename(combined_masks+ "FINAL-combined_{}-bin.nii.gz".format(mask))
            except:
                pass
            if "first" in mask:
                cmd = ["fslmaths", get_first(mse_long[0]), "-dilM", "-mul", combined_masks+ "FINAL-combined_{}-bin.nii.gz".format(mask), combined_masks+ "FINAL-combined_{}.nii.gz".format(mask)]
                Popen(cmd).wait()
            print("COMBINED FILE --check ", combined_masks+ "FINAL-combined_first.nii.gz")

        # create individual deep gray nifits (thal, puta, etc, from first segmentation)
        if os.path.exists(combined_masks+ "FINAL-combined_first.nii.gz"):
            isolate_first(combined_masks+ "FINAL-combined_first.nii.gz", combined_masks)




def isolate_first(first_mask, combined_masks):
    masks = {"L-Thal" :10, "L-Caud":11, "L-Put":12, "L-Pall":13, "L-Hippo":17, "L-Amyg":18, "L-Accum":26,\
            "R-Thal":49, "R-Caud":50, "R-Put":51, "R-Pall":52, "R-Hippo":53, "R-Amyg":54, "R-Accum":58,  "BrainStem":16}
    for area in masks:
        num = masks[area]
        print(area,num )
        low = num - .1
        high = num + .1
        cmd = ["fslmaths",first_mask, "-thr", str(low), "-uthr", str(high),"-bin", combined_masks + 'FINAL-combined_{}-bin.nii.gz'.format(area)]
        print(cmd)
        Popen(cmd).wait()

def mult_jacobian(mse_list,reg_to_bl, combined_masks, jacobian_masks):
    if len(mse_list)>0:
        bl_mse = mse_list[0]
        other_mse = mse_list[1:]
        for mse in other_mse:
            jacobian = reg_to_bl + mse + "_jacobian_" + bl_mse + ".nii.gz"
            if os.path.exists(jacobian):
                if not os.path.exists(jacobian_masks):os.mkdir(jacobian_masks)
                if not os.path.exists(jacobian_masks +'/'+ mse): os.mkdir(jacobian_masks+'/'+mse)
                for seg in os.listdir(combined_masks):
                    if seg.startswith("FINAL") and "bin" in seg:
                        jaco_mask = jacobian_masks +'/'+ mse +"_" + bl_mse + '/'+ seg.replace("bin.", "jacobian.")
                        print("XXXXXXXXXXXXXXXXX","fslmaths", jacobian, "-mul", combined_masks + seg,jaco_mask  )
                        cmd = ["fslmaths", jacobian, "-mul", combined_masks + seg,jaco_mask ]
                        Popen(cmd).wait()
                        #os.symlink(jaco_mask, "{}/{}/jacobian/".format(_get_output(mse), mse))

def run_all(mse, mse_list):
    long_dir = config["long_output_directory"] +"/"+msid
    jacobian_dir = long_dir +'/jacobian/'
    reg_to_bl = jacobian_dir + "/reg_to_bl/"
    combined_masks = jacobian_dir +'/combined_masks/'
    jacobian_masks = jacobian_dir +'/jacobian_masks/'
    if not os.path.exists(long_dir):os.mkdir(long_dir)

    #register all T1's and corresponding masks (sienax, first) to the baseline space
    reg_to_BL(mse_list, msid, jacobian_dir, reg_to_bl, combined_masks)

    #combineing and averaging all the masks
    combine_masks(mse_list, combined_masks)

    #multiply combined masks to the jacobian matrix produced by the reg_to_BL scripts
    mult_jacobian(mse_list, reg_to_bl, combined_masks, jacobian_masks)

    #delete registered (non-averaged) masks

    for items in os.listdir(combined_masks):
        if not items.startswith("FINAL") and not items.endswith("temp"):
            os.remove(combined_masks + items)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))
    ms = "ms1048"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            mse_list.append(mse)
        else:
            print(mse_list, msid)
            run_all(msid, mse_list)
            ms = msid
            mse_list = []
        #print(msid, mse_list)
        # initializing the output directories






"""if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ms', nargs="+")
    args = parser.parse_args()
    msid = args.ms[0]

    print("msid is:", msid)
    text_file = '/data/henry6/gina/all_txt/{0}.txt'.format(msid)
    print(text_file)

    if os.path.exists(text_file):
        with open(text_file,'r') as f:
            mse_lines = f.readlines()
            mse_list = []
            for mse in mse_lines:
                mse = mse.replace("\n","")
                mse_list.append(mse)

        # initializing the output directories
        long_dir = config["long_output_directory"] +"/"+msid
        jacobian_dir = long_dir +'/jacobian/'
        reg_to_bl = jacobian_dir + "/reg_to_bl/"
        combined_masks = jacobian_dir +'/combined_masks/'
        jacobian_masks = jacobian_dir +'/jacobian_masks/'
        if not os.path.exists(long_dir):os.mkdir(long_dir)

        #register all T1's and corresponding masks (sienax, first) to the baseline space
        reg_to_BL(mse_list, msid, jacobian_dir, reg_to_bl, combined_masks)

        #combineing and averaging all the masks
        combine_masks(mse_list, combined_masks)

        #multiply combined masks to the jacobian matrix produced by the reg_to_BL scripts
        mult_jacobian(mse_list, reg_to_bl, combined_masks, jacobian_masks)

        #delete registered (non-averaged) masks
        for items in os.listdir(combined_masks):
            if not items.startswith("FINAL") and not items.endswith("temp"):
                os.remove(combined_masks + items)"""
