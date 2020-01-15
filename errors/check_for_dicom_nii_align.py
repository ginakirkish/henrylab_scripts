import pandas as pd
import argparse
import csv
import pandas as pd
import pbr
import os
import pandas as pd
from glob import glob
from pbr.base import _get_output
import json



def get_dicom(mse):
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*".format(mse))[0]
        print("DICOM DIRECTORY:", dicom)
        if not os.path.exists(dicom):
            dicom = ""
    except:
        dicom = ""
        pass
    return dicom


def get_nifti(mse):
    nifti = _get_output(mse)+"/"+mse+"/nii/status.json"
    if not os.path.exists(nifti):
        print("NIFTI DIRECTORY DOES NOT EXIST")
        nifti = ""
    else:
        print("NIFTI DIECTORY:", nifti)
    return nifti


def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if not os.path.exists(align):
        print("ALIGN DIRECTORY DOES NOT EXIST")
        align = ""

    else:
        print("NIFTI DIECTORY:", align)
    return align

def get_baseline_mni(mse):
    bl = _get_output(mse)+"/"+mse+"/alignment/baseline_mni/"
    if not os.path.exists(bl):
        print("baseline mni DIRECTORY DOES NOT EXIST")
        bl = ""
    else:
        print("NIFTI DIECTORY:", bl)
    return bl

def get_sienax(mse):
    sienax_flair = _get_output(mse)+"/"+mse+"/sienax_flair/"
    sienax_t2 = _get_output(mse)+"/"+mse+"/sienax_t2/"
    if os.path.exists(sienax_flair):
        sienax = sienax_flair
    elif os.path.exists(sienax_t2):
        sienax = sienax_t2
    else:
        sienax = ""
    return sienax


def check_spinal_cord(c, o):
    print("running...")
    writer = open("{}".format(o), "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mse", "Error"])
    spreadsheet.writeheader()
    df = pd.read_csv("{}".format(c))
    towrite = {}
    for _, row in df.iterrows():
        msid = row['msid']
        mse = row['mse']
        print(mse)
        towrite["msid"] = msid
        towrite["mse"] = mse
        towrite["Error"] = ""

        if len(get_sienax(mse)) < 1:
            towrite["Error"] = "no sienax"

        if len(get_baseline_mni(mse)) < 1:
            towrite["Error"] = "no baseline mni"

        if len(get_align(mse)) < 1:
            towrite["Error"] = "no align"


        if len(get_nifti(mse)) > 1:
            with open(get_nifti(mse)) as data_file:
                data = json.load(data_file)

                if len(data["t1_files"]) == 0:
                    towrite["Error"] = "no T1 file"
                else:
                    t1_file = data["t1_files"][-1].split('/')[-1]
                    print(t1_file)
                if len(data["t2_files"]) == 0:
                    if len(data["flair_files"]) == 0:
                        towrite["Error"] = "no T2 or FLAIR file"

                else:
                    t2_file = data["t2_files"][-1].split('/')[-1]
                    print(t2_file)
        else:
            towrite["Error"] = "no nifti"

        if len(get_dicom(mse)) < 1:

            towrite["Error"] = "no dicom"



        spreadsheet.writerow(towrite)
    writer.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for the nifti, align, and dicom pipelines aas well as checking for a t1 in the nifti status file')
    parser.add_argument('-i', help = 'csv containing the msid')
    parser.add_argument('-o', help = 'output directory')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    o = args.o
    print(c, o)
    check_spinal_cord(c, o)

