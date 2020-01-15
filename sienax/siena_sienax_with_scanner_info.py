import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
from subprocess import PIPE, Popen

def get_align(mse):
    mse = str(mse)
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align



def run_siena_sienax(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx,'mse']
        date = df.loc[idx, 'date']
        siena_long = "/data/henry10/PBR_long/subjects/" + str(msid) + "/siena_optibet/"
        #siena_path = str(df.loc[idx, 'siena_path'])
        #print(siena_path)

        pbvc = df.loc[idx, 'PBVC']
        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):
                    df.loc[idx,"siena_path"] = mse_siena
                    mse2 = "mse" + mse_siena.split("mse")[2].replace("_","")
                    df.loc[idx, "mse2"] = mse2
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                    if not os.path.exists(siena_report):
                        continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                df.loc[idx, 'PBVC'] =  line.split()[1]
                    if os.path.exists(_get_output(mse2)+"/"+mse2+"/nii/status.json"):
                        with open(_get_output(mse2)+"/"+mse2+"/nii/status.json") as data_file:
                            data = json.load(data_file)
                            if len(data["t1_files"]) > 0:
                                t1_filemse2 = data["t1_files"][-1].split('/')[-1].split("-")[3].split(".nii.gz")[0]
                                df.loc[idx, "T1 - mse2"] = t1_filemse2
                    try:
 
                        cmd = ["ms_get_phi", "--examID", mse2, "-p", password]
                        proc = Popen(cmd, stdout=PIPE)
                        output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])

                        scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
                        #print("scan date", scan_date)
                        df.loc[idx, "ScanDate - mse2"] = scan_date

                        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse2))[0]
                        cmd = ["dcmdump", dicom]
                        proc = Popen(cmd, stdout=PIPE)
                        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                        x = ["SoftwareVersions", "BodyPartExamined", "StationName"]
                        for line in output:
                            for flag in x:
                                if flag in line:
                                    dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                                    #print(flag,":", dicom_info)
                                    if flag == "SoftwareVersions":
                                        df.loc[idx,"SoftwareVersions - mse2"] = dicom_info
                                    if flag == "StationName":
                                        df.loc[idx,"StationName - mse2"] = dicom_info


                    except:
                        pass



        """

        siena_long = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'

        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):

                    df.loc[idx, 'siena'] = mse_siena
                    mse1 =  "mse" + mse_siena.split("mse")[1].split("_")[0]
                    mse2 = "mse" + mse_siena.split("mse")[2]
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                    if not os.path.exists(siena_report):
                        continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                df.loc[idx, 'PBVC'] = line.split()[1]
                    if os.path.exists(get_align(mse2)):
                        with open(get_align(mse2)) as data_file:
                            data = json.load(data_file)
                        if len(data["t1_files"]) == 0:
                            continue
                        else:
                            t1_file2 = data["t1_files"][-1].split('/')[-1]
                            df.loc[idx, 'T1_2'] = t1_file2


        if os.path.exists(get_align(mse)):
            print(get_align(mse))
            with open(get_align(mse)) as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
            else:
                t1_file = data["t1_files"][-1].split('/')[-1]
                df.loc[idx, 'T1_1'] = t1_file"""

        sienaxfl =  _get_output(mse) + '/' + mse + '/sienaxorig_flair/'
        sienaxt2 =  _get_output(mse) + '/' + mse + '/sienaxorig_t2/'
        sienaxt1 =  _get_output(mse) + '/' + mse + '/sienaxorig_t1/'
        sienaxnoles =  _get_output(mse) + '/' + mse + '/sienaxorig_noles/'
        if os.path.exists(sienaxfl):
            sienax = sienaxfl
            df.loc[idx, "SIENAX"] = "sienaxorig_flair"
        elif os.path.exists(sienaxt2):
            sienax = sienaxt2
            df.loc[idx,"SIENAX"] = "sienaxorig_t2"
        elif os.path.exists(sienaxt1):
            sienax = sienaxt1 
            df.loc[idx, "SIENAX"] = "sienaxorig_t1"
        elif os.path.exists(sienaxnoles):
            sienax = sienaxnoles
            df.loc[idx,"SIENAX"] = "sienaxorig_noles"
        else:
            sienax = ""

        base_dir = sienax
        print(base_dir)
        if os.path.exists(base_dir):


            print(base_dir)
            report = base_dir + "/report.sienax"
            print(report)
            with open(report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                    if not len(line) >= 1:
                        continue
                    if line.startswith("VSCALING"):
                        df.loc[idx, 'vscale'] = line.split()[1]
                    elif line.startswith("pgrey"):
                        df.loc[idx, 'cortical col (u, mm3)'] = line.split()[1]
                    elif line.startswith("vcsf"):
                        df.loc[idx, 'vCSF vol (u, mm3)'] = line.split()[1]
                    elif line.startswith("GREY"):
                        df.loc[idx, 'GM vol (u, mm3)'] = line.split()[1]
                    elif line.startswith("WHITE"):
                        df.loc[idx, 'WM vol (u, mm3)'] = line.split()[1]
                    elif line.startswith("BRAIN"):
                        df.loc[idx, 'brain vol (u, mm3)'] = line.split()[1]
            if os.path.exists(base_dir + '/lesion_mask.nii.gz'): 

                lm = base_dir +  "/lesion_mask.nii.gz"
                img = nib.load(lm)
                data = img.get_data()
                df.loc[idx, 'lesion vol (u, mm3)'] = np.sum(data)

                print(np.sum(data))

        if os.path.exists(get_align(mse)):
                with open(get_align(mse)) as data_file:
                    data = json.load(data_file)
                    if len(data["t1_files"]) > 0:
                        t1_file = data["t1_files"][-1].split('/')[-1]
                        df.loc[idx, 'T1'] = t1_file 
                    if len(data["t2_files"]) > 0:
                        t2_file = data["t2_files"][-1].split('/')[-1]
                        df.loc[idx, 'T2'] = t2_file 
                    if len(data["flair_files"]) > 0:
                        flair_file = data["flair_files"][-1].split('/')[-1]
                        df.loc[idx, 'FLAIR'] = flair_file 

        #dicom = ""
        try:
            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
            cmd = ["dcmdump", dicom]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            x = ["SoftwareVersions", "BodyPartExamined", "StationName", "TransmitCoilName", "ReceiveCoilName"]
            for line in output:
                for flag in x:
                    if flag in line:

                        dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                        print(flag,":", dicom_info)

                        if flag == "SoftwareVersions":
                            df.loc[idx,"SoftwareVersions"] = dicom_info
                        if flag == "BodyPartExamined":
                            df.loc[idx,"BodyPartExamined"] = dicom_info
                        if flag == "StationName":
                            df.loc[idx,"StationName"] = dicom_info
                        if flag == "TransmitCoilName":
                            df.loc[idx,"TransmitCoilName"] = dicom_info
                        if flag == "ReceiveCoilName":
                            df.loc[idx,"ReceiveCoilName"] = dicom_info

        except:
            df.loc[idx, "dicom"] = "no dicom in working directory"
            pass
        df.to_csv("{0}".format(out))







if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    #parser.add_argument('-s', help = 'PBR directory name i.e., sienax_flair ')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    run_siena_sienax(c,out)




