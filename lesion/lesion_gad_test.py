import os
from glob import glob
import subprocess
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
from nipype.interfaces.fsl import RobustFOV, Reorient2Std
from nipype.interfaces.c3 import C3dAffineTool
import argparse
from getpass import getpass
from nipype.interfaces.fsl import BinaryMaths, UnaryMaths, ErodeImage, ImageStats, Threshold, DilateImage
import shutil


PBR_base_dir = '/data/henry7/PBR/subjects/'

password = getpass("mspacman password: ")

"""def get_tps(msid,mse):
    filepath = '/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/EPIC_ms/{0}.txt'.format(msid)
    if os.path.exists(filepath):
        with open(filepath,'r') as f:
            timepoints = f.readlines()
            mse_bl = timepoints[0].replace("\n","")
            info = [msid, mse_bl, mse]
            return info
    else:
        print ("no msid tracking txt file exists")
        return False

class imageData():
    def __init__(self, t1_file, gad_file):
        self.t1_file = t1_file
        self.gad_file = gad_file"""

def run_pbr_align(mse):
    alignment_folder = "/data/henry7/PBR/subjects/{0}/alignment".format(mse)
    if os.path.exists(alignment_folder):
        cmd_rm = ['rm','-r', alignment_folder]
        print (cmd_rm)
        proc = Popen(cmd_rm)
        proc.wait()
    cmd = ['pbr', mse, '-w', 'align', '-R', "-ps", password]
    print (cmd)
    proc = Popen(cmd)
    proc.wait()

"""def file_label(mse):
    if not os.path.exists(PBR_base_dir+"/"+mse+"/alignment/status.json"):
        run_pbr_align(mse)
    with open(PBR_base_dir+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            print("no {0} t1 files".format(tp))
            run_pbr_align(mse)
            t1_file = "none"
        else:
            t1_file = data["t1_files"][-1]

        if len(data["gad_files"]) == 0:
            print("no {0} gad files".format(tp))
            gad_file ="none"
        else:
            gad_file = data["gad_files"][-1]


    if t1_file == "none":
        if count > 3:
            print ("Error in status.json file, T1 not being categorized correctly")
        else:
            count += 1
            file_label(mse,tp,count)
    else:
        return imageData(t1_file, gad_file, bl_t1_mni)"""

def gad_diff_map(mse):
    if not os.path.exists(PBR_base_dir+"/"+mse+"/alignment/status.json"):
        run_pbr_align(mse)
    with open(PBR_base_dir+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            run_pbr_align(mse)
            t1_file = "none"
        else:
            t1_file = data["t1_files"][-1]

        if len(data["gad_files"]) == 0:
            gad_file ="none"
            print("does not have GAD file to produce map")
        else:
            gad_file = data["gad_files"][-1]






            enhance_path = PBR_base_dir+ mse+ "/enhancement_mask"
            lesion_sienax = PBR_base_dir + mse + "/sienax_lst/lesion_mask.nii.gz"
            wm_mask = PBR_base_dir + mse + "/sienax_lst/I_stdmaskbrain_pve_2.nii.gz"
            wm_bin = enhance_path + "/wm.nii.gz"
            gad_diff = enhance_path + "/gad_diff_map.nii.gz"
            if os.path.exists(lesion_sienax) and os.path.exists(wm_mask):
                if not os.path.exists(enhance_path):
                    os.mkdir(enhance_path)



                    cmd = ["fslmaths",lesion_sienax, "-bin", enhance_path + "/lesion_bin.nii.gz"]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    print("binary lesion mask has been created")

                    cmd = ["fslmaths",lesion_sienax, "-add", wm_mask, "-bin", wm_bin]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    print("wm mask has been created")


                    cmd = ["fslmaths",gad_file, "-sub", t1_file, "-div", t1_file, "-mul", "-1", "-mul", wm_bin, gad_diff]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    print("gad difference map has been created")

                    cmd = ["fslstats", gad_diff, "-M", "-S"]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    median = (output[0])[0]
                    std_dev = (output[0])[1]
                    print("Median of the white matter difference map is:",median)
                    print("Standard deviation of the white matter difference map is:",std_dev)

                    cmd = ["fslmaths", gad_diff, "-sub", median, "-div", std_dev,"-mul",enhance_path + "/lesion_bin.nii.gz", "-uthr", "-5", "-mul", "-1", "-bin",  enhance_path + "/enhanced_lesion_mask.nii.gz"]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]



def check_mni_angulated_folder(mse):
    filepath = '/data/henry7/PBR/subjects/{0}/alignment/mni_angulated'.format(mse)
    if os.path.exists(filepath):
        print ("mni_angulated folder for {0} exists".format(mse))
        check = True
    else:
        print ("mni_angulated folder for {0} does not exist, fixing the issue".format(mse))
        run_pbr_align(mse)
        print ("mni_angulated folder for {0} exists".format(mse))
        check = False
    return check





def create_gad_enhancement(mse):
    check_mni_angulated_folder(mse)
    #tp = file_label(info[1])
    gad_diff_map(mse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mse', nargs="+")
    args = parser.parse_args()
    mse = args.mse[0]
    #outdir = cc["output_directory"]
    print("mse is:", mse)
    create_gad_enhancement(mse)
    print ("{}'s GAD ENHANCMENT map complete".format(mse))

