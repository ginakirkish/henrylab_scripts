import numpy as np
import os
import pandas as pd
import argparse
from subprocess import Popen, PIPE
from glob import glob
import csv
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
import math

recon_dir = "/data/henry6/PBR/surfaces/"
no_wm = "/data/henry6/PBR/surfaces/MNI152_T1_1mm/mri/no_wm_MNI_new.nii.gz"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    print(mse)
    try:
        recon = glob(recon_dir + "*{0}*".format(mse))[0]
        print(recon)

    except:
        print(mse, "freesurfer file does not exist")
        cmd = ["pbr", mse, "-w", "recon", "-R"]
        Popen(cmd).wait()
        pass

    if os.path.exists(recon):
        recon_seg = recon + "/mri/aparc+aseg.mgz"
        t1 = recon.split("/")[-1]
        t1_mni = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/" + t1 + "_T1mni.nii.gz"
        print(t1_mni)
        if os.path.exists(t1_mni):
            t1_mni_optibet = t1_mni.replace(".nii", "_optiBET_brain.nii")
            msid = t1.split("-")[0]
            msid_long = "/data/henry11/PBR_long/subjects/" + msid
            t1_lesion_long = msid_long + "/t1_lesion_mni/"
            recon_nii = recon_seg.replace(".mgz", ".nii.gz")
            recon_reorient = recon_nii.replace(".nii", "_reorient.nii")
            recon_register = t1_mni.replace(".nii", "_aparc+aseg.nii")
            t1mni_lesion = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/t1_lesion.nii.gz"
            sienax_t1recon = _get_output(mse) + "/" + mse + "/sienax_t1recon/"
            wm_mask = sienax_t1recon + "I_stdmaskbrain_pve_2.nii.gz"
            gm_mask = sienax_t1recon + "I_stdmaskbrain_pve_1.nii.gz"

            print(recon, t1, msid, t1_mni)
            print("getting t1 lesion...")

            cmd = ["mri_convert", recon_seg, recon_nii]
            print(cmd)
            Popen(cmd).wait()

            cmd = ["fslreorient2std", recon_nii, recon_reorient]
            print(cmd)
            Popen(cmd).wait()
            print(t1_mni_optibet)

            if not os.path.exists(t1_mni_optibet):

                cmd = ["optiBET.sh", "-i", t1_mni,"-o", t1_mni_optibet]
                print(cmd)
                Popen(cmd).wait()

            if not os.path.exists(recon_register):
                cmd = ["flirt","-interp", "nearestneighbour", "-dof", "6", "-in", recon_reorient, "-ref", t1_mni_optibet, "-out", recon_register]
                print(cmd)
                Popen(cmd).wait()


            cmd = ["fslmaths", recon_register, "-thr", "76.5", "-uthr", "77.5", t1mni_lesion]
            print(cmd)
            Popen(cmd).wait()


            if not os.path.exists(sienax_t1recon):
                cmd = ["sienax_optibet",  t1_mni, "-lm",t1mni_lesion, "-r", "-d", "-o", sienax_t1recon]
                print(cmd)
                Popen(cmd).wait()
        else:
            print(t1_mni, "this file does not exist")
