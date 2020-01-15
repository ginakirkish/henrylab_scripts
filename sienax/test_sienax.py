from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import pbr
from pbr.workflows.nifti_conversion.utils import description_renamer
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]



df = pd.read_csv("/home/sf522915/EPIC1_FINAL_ADAMSLIST_WITHMSE_FINAL.csv")
def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in heuristic.keys():
            if heuristic[desc] == nii_type:
                output.append(desc)
    return output


writer = open("/home/sf522915/EPIC1_FINAL_ADAMSLIST_WITHMSE_NEW7.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["msID", "mseID", "EPIC_Project", "VisitType", "Brain_MRI_Date","scanner",\
                                                 "sienax_flair", "sienax_t2", "T1", "T2", "FLAIR", \
                                                 "vscale",
                                                 "brain vol (u, mm3)",
                                                 "WM vol (u, mm3)",
                                                 "GM vol (u, mm3)",
                                                 "vCSF vol (u, mm3)",
                                                 "cortical vol (u, mm3)",
                                                 "lesion vol (u, mm3)" ])
spreadsheet.writeheader()


for _, row in df.iterrows():
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    mse = row["mseID"]
    print(msid)
    acc = row["Accession_Number"]
    date = int(row['Brain_MRI_Date'])
    EPIC = row["EPIC_Project"]
    visit = row["VisitType"]
    sienax_flair = ""
    sienax_t2 = ""
    t1_file = ""
    t2_file = ""
    flair_file = ""
    vscale = ""
    brain = ""
    wm = ""
    gm = ""
    csf = ""
    cortical = ""
    lesion = ""
    scanner = ""
    row = {"msID": msid, "mseID": mse, "EPIC_Project": EPIC, "VisitType": visit,\
            "Brain_MRI_Date": date }
    print(row)


    if msid.startswith("ms"):
        if os.path.exists(_get_output(mse)+ "/" + mse + "/sienax_flair"):

            sienax_flair = "sienax_flair"
            list = os.listdir(_get_output(mse)+'/'+mse+"/sienax_flair/") # dir is your directory path
            number_files = len(list)
            if number_files > 30:
                report = os.path.join(_get_output(mse), mse, "sienax_flair/report.sienax")
                with open(report, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
                    for line in lines:
                        if line.startswith("VSCALING"):
                            vscale =  line.split()[1]

                        elif line.startswith("pgrey"):
                            cortical = line.split()[2]
                        elif line.startswith("vcsf"):
                            csf = line.split()[2]
                        elif line.startswith("GREY"):
                            gm = line.split()[2]
                        elif line.startswith("WHITE"):
                            wm = line.split()[2]
                        elif line.startswith("BRAIN"):
                            brain = line.split()[2]

                lm = os.path.join(_get_output(mse), mse, "sienax_flair/lesion_mask.nii.gz")
                img = nib.load(lm)
                data = img.get_data()
                lesion = np.sum(data)




        elif os.path.exists(_get_output(mse) + "/" + mse + "/sienax_t2"):
            sienax_t2 = "sienax_t2"
            list = os.listdir(_get_output(mse)+ '/' + mse + "/sienax_t2/") # dir is your directory path
            number_files = len(list)
            if number_files > 30:
                report = os.path.join(_get_output(mse), mse, "sienax_t2/report.sienax")
                with open(report, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
                    for line in lines:
                        if line.startswith("VSCALING"):
                            vscale =  line.split()[1]
                        elif line.startswith("pgrey"):
                            cortical = line.split()[2]
                        elif line.startswith("vcsf"):
                            csf = line.split()[2]
                        elif line.startswith("GREY"):
                            gm = line.split()[2]
                        elif line.startswith("WHITE"):
                            wm = line.split()[2]
                        elif line.startswith("BRAIN"):
                            brain = line.split()[2]


                lm = os.path.join(_get_output(mse), mse, "sienax_t2/lesion_mask.nii.gz")
                img = nib.load(lm)
                data = img.get_data()
                lesion = np.sum(data)
        else:
            row = { "msID": msid, "mseID": mse, "EPIC_Project": EPIC, "VisitType": visit,\
            "Brain_MRI_Date": date, "sienax_flair" : sienax_flair, "sienax_t2": sienax_t2, "T1": t1_file, "T2": t2_file, "FLAIR": flair_file, \
            "vscale": vscale,
            "brain vol (u, mm3)": brain,
            "WM vol (u, mm3)" : wm,
            "GM vol (u, mm3)": gm,
            "vCSF vol (u, mm3)": csf,
            "cortical vol (u, mm3)": cortical,
            "lesion vol (u, mm3)": lesion}
            print(row)
            #spreadsheet.writerow(row)


        def get_modality(mse, nii_type="T1"):
            output = pd.DataFrame(index=None)
            num = mse.split("mse")[-1]
            cmd = ["ms_dcm_exam_info", "-t", num]
            proc = Popen(cmd, stdout=PIPE)
            lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
            if nii_type:
                files = filter_files(lines, nii_type, heuristic)
                output["nii"] = files
            else:
                output["nii"] = lines
            output["mse"] = mse
            return output
        get_modality(mse, "T1")


        with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1])
                series = t1_file.split("-")[2].lstrip("0")
                if not len(series) > 0:
                    series = "1"
                dcm = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))
                if len(dcm) > 0 :
                    dcm = dcm[0]
                    cmd = ["dcmdump", dcm]
                    proc = Popen(cmd, stdout=PIPE)

                    lines = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
                    row["scanner"] = lines
                    if "qb3-3t" in lines:
                        scanner = "qb3"
                    elif "SIEMENS" in lines:
                        scanner = "Skyra"
                    elif "CB3TMR"  or "CB-3TMR" in lines:
                        scanner = "CB"
                    else:
                        scanner = "unknown"
                    row = {"scanner": scanner}
                    print(row)


            if len(data["t2_files"]) == 0:
                row = {"T2": "NONE"}
            else:
                t2_file = data["t2_files"][-1]
                t2_file = (t2_file.split('/')[-1])
                row = {"T2": t2_file}
            if len(data["flair_files"]) == 0:
                row = {"FLAIR": "NONE"}
            else:
                flair_file = data["flair_files"][-1]
                flair_file = (flair_file.split('/')[-1])
                row = {"FLAIR": flair_file}



    row = { "msID": msid, "mseID": mse, "EPIC_Project": EPIC, "VisitType": visit,\
            "Brain_MRI_Date": date, "sienax_flair" : sienax_flair, "sienax_t2": sienax_t2, "T1": t1_file, "T2": t2_file, "FLAIR": flair_file, \
            "vscale": vscale,
            "brain vol (u, mm3)": brain,
            "WM vol (u, mm3)" : wm,
            "GM vol (u, mm3)": gm,
            "vCSF vol (u, mm3)": csf,
            "cortical vol (u, mm3)": cortical,
            "lesion vol (u, mm3)": lesion}
    print(row)
    spreadsheet.writerow(row)
writer.close()