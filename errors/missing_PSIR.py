
import os
import pandas as pd
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer




def check_pacman(mse):
    pacman = ""
    num = mse.split("mse")[-1]
    #print("ms_dcm_exam_info", "-t", num, "-D")
    cmd = ["ms_dcm_exam_info", "-t", num, "-D"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    if "C2_3_2Fl_seg_psir_TI_PSIR" in lines:
        pacman = True
    elif "C2-3_2Fl_seg_psir_TI_PSIR" in lines:
        pacman = True
    else:
        pacman = False
    return pacman

def check_dicom(mse):
    dcm = ""
    dicom = glob("/working/henry_temp/PBR/dicoms/{}/E*/".format(mse))
    if len(dicom) == 1:
        dicom = dicom[0]
        dicom2 = ""
    elif len(dicom) == 2:
        dicom = dicom[0]
        dicom2 = dicom[1]
    else:
        dicom = ""
        dicom2 = ""
    dicoms = [dicom, dicom2]
    for d in dicoms:
        try:
            cmd = ["dti_info", dicom]
            proc = Popen(cmd, stdout=PIPE)
            lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
            if "C2_3_2Fl_seg_psir_TI_PSIR" in lines:
                dcm = True
            else:
                continue
        except:
            pass
    return dcm

def check_nii(mse):
    nifti = ""
    nii = "{}/{}/nii/".format(_get_output(mse),mse)
    if os.path.exists(nii):
        for series in os.listdir(nii):
            #print(series)
            if "C2_3_2Fl_seg_psir_TI_PSIR" in series:
                nifti = True
            else:
                x = True
    else:
        nifti = "Nifti not run"
    return nifti


#csv = '/home/sf522915/Downloads/missingPSIRtps.csv'
#o = '/home/sf522915/Downloads/missing-PSIR.csv'

#csv = "/home/sf522915/Downloads/EPIC1_C1A.csv"
#o = "/home/sf522915/Downloads/EPIC1_C1A-mse.csv"
#csv = "/home/sf522915/Documents/ANTJE-check-PSIR.csv"
csv = "/home/sf522915/Documents/ANTJE-check-PSIR-data-new.csv"
o = "/home/sf522915/Documents/ANTJE-check-PSIR-data-new-oct21-nii.csv"





df = pd.read_csv("{}".format(csv))
for idx in range(len(df)):
    msid = df.loc[idx, "msid"]
    mse = df.loc[idx, "mse"]
    date = df.loc[idx, "date"]
    #df.loc[idx, "C2_3 - MSPACMAN"] = check_pacman(mse)
    #df.loc[idx, "C2_3 - DICOM"] = check_dicom(mse)
    df.loc[idx, "C2_3 - NIFTI"] = check_nii(mse)

"""


    #print(msid)
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.split("ms")[1].lstrip("0"), "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    for m in lines:
        try:
            mse = "mse" + m[0]
            date = m[1]
        except:
            pass
        #print(mse, date)
        if len(mse) > 4 and len(mse) < 10 and not "Valid" in mse:
            #df.append({"mse": mse},ignore_index=True)
            #df.loc[idx, "mse"] = mse
            #for idx, in mse:
            print(msid +"_" +mse+"_"+ date)
            df.loc[idx, "msid-mse"] = msid + "_" + mse
            df.loc[idx, "date"] = date
            #df.loc[idx, "C2_3 - MSPACMAN"] = check_pacman(mse)
            #df.loc[idx, "C2_3 - DICOM"] = check_dicom(mse)
            #df.loc[idx, "C2_3 - NIFTI"] = check_nii(mse)"""
df.to_csv("{}".format(o))
