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

def create_t1_lesions(mse_mni, msid, t1_bl_mni, t1mni_lesion, wm_mask, gm_mask):


    base_dir = _get_output(mse) + "/" + mse + "/t1_les_long/"
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    wm_with_les = base_dir + "/wm_withles.nii.gz"
    wm_eroded = base_dir + "/wm_ero.nii.nii.gz"
    lesion_dil = base_dir + "/les_dil.nii.gz"
    wm_t1 = base_dir + "/wm_t1.nii.gz"
    wm_uhalf = base_dir + "/wm_Uhalf.nii.gz"

    lesion_mul_t1 = base_dir + "/lesion.nii.gz"
    prob_map = base_dir +"/prob_map_new.nii.gz"
    prob_map_nobs = base_dir +"/prob_map_nowmbs.nii.gz"
    final_lesion = _get_output(mse) + "/" + mse + "/sienax_t1recon/lesion_final_new.nii.gz"
    wm_no_bs = base_dir+ "/wm_no_bs.nii.gz"

    cmd = ["fslmaths", wm_mask, "-add", t1mni_lesion, "-bin", wm_with_les]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", t1_bl_mni,"-w", wm_mask, "-o", t1_bl_mni.replace(".nii.gz", "_n4corr.nii.gz")]
    print(cmd)
    Popen(cmd).wait()


    cmd = ["fslmaths", wm_mask, "-ero","-sub", no_wm, "-thr", ".1", "-mul",t1_bl_mni, wm_eroded]
    print(cmd)
    Popen(cmd).wait()


    cmd = ["fslstats", wm_eroded, "-P", "50"]
    print(cmd)
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    print(output, "THIS IS THE OUTPUT FILE")
    output = output[0]
    median_nawm = float(output[0])
    print(median_nawm, "THIS IS THE MEDIAN of the NAWM")


    #dilating the lesion mask and subtracting the gray matter
    cmd = ["fslmaths",t1mni_lesion , "-dilM",  "-sub", gm_mask,"-thr", ".1","-bin", lesion_dil]
    print(cmd)
    Popen(cmd, stdout=PIPE).wait()

    cmd = ["fslmaths", lesion_dil, "-add", wm_mask, "-bin","-ero", wm_with_les]
    print(cmd)
    Popen(cmd).wait()
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    cmd = ["fslmaths", wm_with_les, "-mul",t1_bl_mni, wm_t1]
    print(cmd)
    Popen(cmd).wait()

    new_median_nawm = median_nawm - .000001
    print("NEW MEDIAN", new_median_nawm)


    cmd = ["fslmaths",  wm_eroded, "-thr", str(new_median_nawm), wm_uhalf]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["fslstats", wm_uhalf, "-S"]
    print(cmd)
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    std_nawm = float(output[0])
    print(std_nawm, "THIS IS THE STANDARD DEVIATION of NAWM")

    est_std = float(std_nawm) * 1.608

    cmd = ["fslstats", wm_eroded, "-V"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    vol_nawm = float(output[0])
    print(vol_nawm, "THIS IS THE VOLUME OF THE NAWM")

    #calculate wm histogram
    std_times2 = std_nawm*std_nawm*2
    print(std_times2, "this is the standard deviation squared times 2")
    part1 = vol_nawm/(math.sqrt(std_times2*(math.pi)))
    print(part1, "this is part1 times 2")
    cmd = ["fslmaths", wm_t1, "-sub",str(median_nawm),"-sqr", "-div", str(std_times2), "-mul", "-1", "-exp", "-mul", str(part1), base_dir+"/wm_hist.nii.gz"]
    print(cmd, "COMMAND")
    proc = Popen(cmd, stdout=PIPE)
    print(cmd)

    # calculating estimated median and standard deviation for lesions


    cmd = ["fslmaths", t1mni_lesion,"-thr", ".1", "-bin", "-mul",t1_bl_mni,  lesion_mul_t1]
    Popen(cmd).wait()
    print(cmd)

    cmd = ["fslstats", lesion_mul_t1, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    print("*****************************")
    median_lesion = float(output[0])
    print(median_lesion, "THIS IS THE LESION MEDIAN")

    new_median_lesion = median_lesion + .000001
    print("NEW MEDIAN", new_median_lesion)

    cmd = ["fslmaths",  lesion_mul_t1, "-uthr", str(new_median_lesion), base_dir+ "/lesion_Lhalf.nii.gz"]
    Popen(cmd).wait()
    print(cmd)

    cmd = ["fslstats",base_dir +"/lesion_Lhalf.nii.gz" , "-S"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    std_lesion = output[0]
    std_lesion = float(std_lesion[0])
    print(std_lesion, "THIS IS THE STANDARD DEVIATION for the lesion lower half")

    est_std = std_lesion * 1.608
    #echo 20.077990*1.608 | bc

    cmd = ["fslstats", lesion_mul_t1 , "-V"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    vol_lesion = float(output[0])
    print(vol_lesion, "THIS IS THE VOLUME OF THE lesion")

    if not vol_lesion == 0.0:
                # lesion histogram
        lesion_times2 = std_lesion*std_lesion*2
        print(lesion_times2, "thisis the standard deviation times 2")
        part2 = vol_lesion/(math.sqrt(lesion_times2*(math.pi)))
        print(part2, "this is part2 times 2")
        cmd = ["fslmaths", wm_t1, "-sub",str(median_lesion),"-sqr", "-div", str(lesion_times2), "-mul", "-1", "-exp", "-mul", str(part1),base_dir+"/lesion_hist.nii.gz"]
        print(cmd, "COMMAND")
        Popen(cmd, stdout=PIPE).wait()
        print(cmd)



        cmd = ["fslmaths", gm_mask, "-dilM","-dilM", base_dir + "/gm_dil.nii.gz"]
        Popen(cmd).wait()
        print(cmd)

        # eroding the wm mask and adding in the dilated lesion mask
        cmd = ["fslmaths",wm_mask,"-sub", no_wm,  "-thr", ".1","-ero","-add",lesion_dil,"-bin", wm_no_bs] # can try adding back later "-sub",gm_MNI,
        Popen(cmd).wait()
        print(cmd)

        # making the probability map
        cmd = ["fslmaths", base_dir+"/lesion_hist.nii.gz", "-add", base_dir+ "/wm_hist.nii.gz",base_dir+"/add_his.nii.gz"]
        Popen(cmd).wait()
        print(cmd)

        print("***************************")

        cmd = ["fslmaths",base_dir +"/lesion_hist.nii.gz", "-div",base_dir+ "/add_his.nii.gz","-mul", wm_with_les, prob_map]
        Popen(cmd).wait()
        print(cmd)

        #or just look in the dialated lesion minus the gray matter mask
        cmd = ["fslmaths",lesion_dil,"-mul",prob_map, "-thr", ".8","-bin","-mul",wm_with_les,"-bin", "-sub", gm_mask, "-thr", ".1", "-bin", "-mul", t1_bl_mni, "-uthrp", "80","-bin", final_lesion]
        Popen(cmd).wait()
        print(cmd)




        #shutil.copyfile(final_lesion, sienax_t1recon + "/lesion_final.nii.gz")
        """
        cmd = ["fslmaths",final_lesion,"-add",  sienax_t1recon + "/lesion_mask.nii.gz",\
               "-add", sienax_t1recon,  "/new_lesion.nii.gz", "-bin", "-mul", t1_bl_mni, "-thrP", "50", sienax_t1recon + "/lesion_final.nii.gz"]
        print(cmd)
        Popen(cmd).wait()

        cmd = ["fslmaths", sienax_t1recon + "/I_stdmaskbrain_seg_1.nii.gz", "-dilM",sienax_t1recon + "/I_stdmaskbrain_seg_1_dil.nii.gz" ]
        Popen(cmd).wait()

        cmd = ["fslmaths", sienax_t1recon + "/lesion_final.nii.gz", "-sub", sienax_t1recon + "/I_stdmaskbrain_seg_1_dil.nii.gz", "-thr", ".1", "-bin", sienax_t1recon + "/lesion_final.nii.gz" ]
        Popen(cmd).wait()"""

        cmd = ["fslview", prob_map, t1_bl_mni,final_lesion ]
        Popen(cmd).wait()


        """
        #if not os.path.exists(PBR_base_dir + "/" + mseid + "/sienax/"):
        cmd = ["sienax_optibet", t1, "_T1mni.nii.gz"), "-lm", base_dir+ "/lesion_prob_map.nii.gz", "-r", "-d", "-o", _get_output(mse) + "/" + mse+ "/sienax_t1/"]
        proc = Popen(cmd)
        proc.wait()"""




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    print(mse)
    try:
        recon = glob(recon_dir + "*{0}*".format(mse))[0]

    except:
        print(mse, "freesurfer file does not exist")
        cmd = ["pbr", mse, "-w", "recon", "-R"]
        Popen(cmd).wait()
        pass

    if os.path.exists(recon):
        recon_seg = recon + "/mri/aparc+aseg.mgz"
        t1 = recon.split("/")[-1]
        t1_bl_mni = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/" + t1 + "_T1mni.nii.gz"

        if os.path.exists(t1_bl_mni):
            t1_bl_mni_optibet = t1_bl_mni.replace(".nii", "_optiBET_brain.nii")
            msid = t1.split("-")[0]
            msid_long = "/data/henry11/PBR_long/subjects/" + msid
            t1_lesion_long = msid_long + "/t1_lesion_mni/"
            recon_nii = recon_seg.replace(".mgz", ".nii.gz")
            recon_reorient = recon_nii.replace(".nii", "_reorient.nii")
            recon_register = t1_bl_mni.replace(".nii", "_aparc+aseg.nii")
            t1mni_lesion = _get_output(mse) + "/" + mse + "/alignment/baseline_mni/t1_lesion.nii.gz"
            sienax_t1recon = _get_output(mse) + "/" + mse + "/sienax_t1recon/"
            wm_mask = sienax_t1recon + "I_stdmaskbrain_pve_2.nii.gz"
            gm_mask = sienax_t1recon + "I_stdmaskbrain_pve_1.nii.gz"

            print(recon, t1, msid, t1_bl_mni)
            print("getting t1 lesion...")

            cmd = ["mri_convert", recon_seg, recon_nii]
            print(cmd)
            Popen(cmd).wait()

            cmd = ["fslreorient2std", recon_nii, recon_reorient]
            print(cmd)
            Popen(cmd).wait()
            print(t1_bl_mni_optibet)

            if not os.path.exists(t1_bl_mni_optibet):

                cmd = ["optiBET.sh", "-i", t1_bl_mni,"-o", t1_bl_mni_optibet]
                print(cmd)
                Popen(cmd).wait()

            if not os.path.exists(recon_register):
                cmd = ["flirt","-interp", "nearestneighbour", "-dof", "6", "-in", recon_reorient, "-ref", t1_bl_mni_optibet, "-out", recon_register]
                print(cmd)
                Popen(cmd).wait()


            cmd = ["fslmaths", recon_register, "-thr", "76.5", "-uthr", "77.5", t1mni_lesion]
            print(cmd)
            Popen(cmd).wait()


            if not os.path.exists(sienax_t1recon):
                cmd = ["sienax_optibet",  t1_bl_mni, "-lm",t1mni_lesion, "-r", "-d", "-o", sienax_t1recon]
                print(cmd)
                Popen(cmd).wait()
            sienax_path = _get_output(mse) + '/' + mse + '/sienax/'
            if os.path.exists(sienax_path):
                cmd = ["fslmaths", sienax_path + 'I_stdmaskbrain_seg_1.nii.gz', "-add", sienax_path + "I_stdmaskbrain_seg_1.nii.gz", sienax_path + "/gmcsf.nii.gz"]
                print(cmd)
                Popen(cmd).wait()

            else:
                print("sienax first run does not exist")
            first = _get_output(mse) + '/' + mse + "/first/"
            if os.path.exists(first):
                first_seg = glob(str(first + "*firstseg.nii.gz"))[0]
                cmd = ["flirt","-interp", "nearestneighbour", "-applyxfm", "-in", first_seg, "-ref", t1_bl_mni, "-init",\
                              _get_output(mse) + '/' + mse + "/alignment/mni_affine.mat", "-out", sienax_path + "first_seg.nii.gz"]
                print(cmd)
                Popen(cmd).wait()

            else:
                cmd = ["pbr", mse, "-w", "first", "-R"]
                print(cmd)
                Popen(cmd).wait()

            cmd = ["fslmaths", sienax_path + "first_seg.nii.gz", "-add", sienax_path + "/gmcsf.nii.gz","-bin", sienax_path + "not_wm.nii.gz"]
            print(cmd)
            Popen(cmd).wait()

            cmd = ["fslmaths", t1mni_lesion, "-sub", sienax_path + "not_wm.nii.gz", "-thr", ".1", "-bin", sienax_path + "/LESION_TEST.nii.gz"]
            print(cmd)
            Popen(cmd).wait()

            """
            cmd = ["fslmaths", sienax_t1recon + 'I_stdmaskbrain_seg_2.nii.gz', "-add",\
                       sienax_t1recon + "lesion_mask.nii.gz", "-mul", sienax_path + "gmcsf.nii.gz",  sienax_t1recon + "/new_lesion.nii.gz" ]
            print(cmd)
            Popen(cmd).wait()"""




            """if not os.path.exists(t1_lesion_long):
                print(t1_lesion_long)
                os.mkdir(t1_lesion_long)
            shutil.copyfile(t1_lesion, t1_lesion_long + msid + "-" + mse + "_t1lesMNI.nii.gz")"""


            mse_mni = mse
            #t1mni_lesion =  sienax_t1recon + "/new_lesion.nii.gz"
            t1mni_lesion =  sienax_path + "/LESION_TEST.nii.gz"
            create_t1_lesions(mse_mni, msid,t1_bl_mni, t1mni_lesion , wm_mask, gm_mask )


        else:
            print(t1_bl_mni, "This path does not exist")