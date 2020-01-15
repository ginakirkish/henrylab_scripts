
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json, uuid
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from subprocess import Popen, PIPE, check_call, check_output
import pandas as pd
import shutil
import csv
import subprocess

base_dir = '/data/henry12/phenoms/Tasmania/'


def check_dim(t1):
    cmd = ["fslhd", t1]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    dim1, dim2, dim3 = "","",""
    for l in output:
        if "pixdim1" in l:
            dim1 = l[-1]
        if "pixdim2" in l:
            dim2 = l[-1]
        if "pixdim3" in l:
            dim3 = l[-1]
    return dim3


def calc_first(seg, num):
    num1 = num - .5
    num2 = num + .5
    cmd = ["fslstats",seg,"-l", "{}".format(num1), "-u","{}".format(num2), "-V"]
    proc = Popen(cmd, stdout=PIPE)
    area = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
    print(seg, area)
    return(area)

def get_first_values(first_path):
    L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS = '','','','','','','','','','','','','','',''
    for files in os.listdir(first_path):
        if files.endswith("firstseg.nii.gz") or files.endswith("firstsegs.nii.gz") and not "_N4_N4" in files:
            print(files)
            seg = first_path + files
            L_thal = calc_first(seg, int(10))
            L_caud = calc_first(seg, 11)
            L_put = calc_first(seg, 12)
            L_pall = calc_first(seg, 13)
            L_hipp = calc_first(seg, 17)
            L_amy = calc_first(seg, 18)
            L_acc = calc_first(seg,26)
            R_thal = calc_first(seg, 49)
            R_caud = calc_first(seg, 50)
            R_put = calc_first(seg, 51)
            R_pall = calc_first(seg, 52)
            R_hipp = calc_first(seg, 53)
            R_amy = calc_first(seg, 54)
            R_acc = calc_first(seg,58)
            BS = calc_first(seg, 16)
            print(L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS)

    return [L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS]


def get_sienax(report):
    VS, PG, VCSF, GM,WM,BV = "","","","","",""
    with open(report, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            if not len(line) >= 1:
                continue
            if line.startswith("VSCALING"):
                VS = line.split()[1]
            elif line.startswith("pgrey"):
                PG = line.split()[2]
            elif line.startswith("vcsf"):
                VCSF = line.split()[2]
            elif line.startswith("GREY"):
                GM = line.split()[2]
            elif line.startswith("WHITE"):
                WM = line.split()[2]
            elif line.startswith("BRAIN"):
                BV = line.split()[2]

    return [ VS, PG, VCSF, GM, WM, BV]

def write_csv(c,out):
    t1 = ""



t1_file = ["AxT1PREVOL","AxT1+CVOL","T1SAG3MM",

"T1TraTIRM+C"]

#              "T1AxSPGR3D","T1axVolSPGR","T1axVOLSPGR","T1axSPGRVOL","AxSPGRAST1.2m","AxSPGR1.2mVol","Ax1.2mVolSPGR",  "AxFSPGR3D",
#"AxT1FLAIR", "T1axFLAIR","t1_tse_sag101"

"""writer = open("/data/henry12/phenoms/csv/Tasmania.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["subject_id",
                                                'Left-Thalamus-Proper',
                                                'Left-Caudate',
                                                "Left-Putamen",
                                                "Left-Pallidum",
                                                "Left-Hippocampus",
                                                "Left-Amygdala",
                                                "Left-Accumbens",
                                                'Right-Thalamus-Proper',
                                                'Right-Caudate',
                                                "Right-Putamen",
                                                "Right-Pallidum",
                                                "Right-Hippocampus",
                                                "Right-Amygdala",
                                                "Right-Accumbens",
                                                "Brain-Stem",
                                                "V Scale",
                                                "pGM",
                                                "CSF",
                                                "GM",
                                                "WM",
                                                "BV"])
"""


def write_csv(c,out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        id = df.loc[idx, 'subjects']
        date = df.loc[idx, "date"]

        print(id, date)
        print("****************")

        for files in os.listdir("{}/{}/iSiteExport/".format(base_dir, id)):
            if files.startswith(str(date)):

                sub_dir = "{}/{}/iSiteExport/{}/".format(base_dir, id,files)

                for nifti in os.listdir(sub_dir):
                    print(sub_dir.split('/')[0])
                    if nifti.startswith("2") and nifti.endswith(".nii.gz"):
                        nii_path = sub_dir+ nifti
                        t1 = nii_path.split('/')[8]
                        print(nifti)
                        if "SPGR" in t1:
                            nii_FINAL = nii_path
                        elif "T1VolumeAquiredSagittal" in t1:
                            nii_FINAL = nii_path
                        elif "AxT1" in t1:
                            nii_FINAL = nii_path
                        elif "3mmT1" in t1:
                            nii_FINAL = nii_path
                        elif "T1" and "3mm" in t1:
                            nii_FINAL = nii_path
                        elif "T1" in t1 and not "CVOL" in t1 and not "SWIT" in t1 and not "CORT1" in t1:
                            nii_FINAL = nii_path
                        else:
                            nii_FINAL = ""
                        try:
                            dim = check_dim(nii_FINAL)
                            if float(dim) < 2:
                                #df.loc[idx, "date"] = nii_FINAL.split("/")[-1].split("_")[0]
                                df.loc[idx, "t1"] = nii_FINAL.split('/')[8].split("_")[-1]
                                df.loc[idx, "dim"] = check_dim(nii_FINAL)
                            else:
                                df.loc[idx, "DIM-LARGE"] = dim
                        except:
                            pass
    df.to_csv('{}'.format(out))




"""for t1 in t1_file:
            t1_dir = glob(str("{}/{}/iSiteExport/20*{}/2*.nii.gz".format(base_dir, id,t1)))
            if len(t1_dir) > 0:
                for t1 in t1_dir:
                    dim = check_dim(t1)
                    if float(dim) < 3.0:
                        date = t1_dir[-1].split("/")[-1].split("_")[0]
                        df.loc[idx, "date"] = date
                        df.loc[idx, 'dimensions'] = dim
                        df.loc[idx, "T1"] = t1
                        print(dim, t1)
                        print("^^^^^^^^^^^^^^^^^^^^^")
                    else:
                        df.loc[idx, "LARGE DIMENSIONS"] = dim"""



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = '')
    parser.add_argument('-o', help = 'output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)

"""subjects = glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/20*/2**.nii.gz")
for t1 in subjects:
    dim = check_dim(t1)

    if float(dim) < 3.0:
        for t1_name in t1_file:
            if t1_name in t1:
                sub_id = t1.split('/')[5]
                date = t1.split("/")[7]
                print(sub_id + "_"+ date)"""





"""subjects = glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/20*/2*N4*.nii.gz")
for t1 in subjects:
    date = t1.split('/')[7].split("_")[0]
    if date.startswith("2010"):
        print(t1.split('/')[5]+ "_" + t1.split('/')[7])"""


t1_file = ["AxFSPGR3D","AxT1PREVOL","AxT1+CVOL","3mmT1sag","3mmSagT1BRAIN","3mmCorT1BRAIN","3mmAxT1BRAIN","T1SAG3MM","T1Cor3mm","T1Ax3mm",
"3mmT1cor","3mmT1ax","T1VolumeAquiredSagittal","T1AxSPGR3D","T1axVolSPGR","T1axVOLSPGR","T1axSPGRVOL","AxSPGRAST1.2m","AxSPGR1.2mVol","Ax1.2mVolSPGR",
"T1TraTIRM+C",
"T13mmCorBrain",
"t1_tse_sag101",
"AxT1FLAIR",
"T1axFLAIR",
"T13mmCorBrain", "SPGR"]

"""for t1 in t1_file:
    subjects =   glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/20*{}/2*.nii.gz".format(t1))
    for file in subjects:
        print(file.split('/')[5]+ "_" + file.split('/')[7])"""


























