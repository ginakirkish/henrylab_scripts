
import argparse
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
import shutil

password = getpass("mspacman password: ")
working = "/working/henry_temp/PBR/dicoms/"
mspac_path = "/data/henry1/mspacman_data/"


def run_dicom(mse):
    try:
        #cmd = ["pbr", mse, "-w", "dicom", "-rps", password,"-R" ]
        cmd = ["ms_dcm_qr2", "-t", mse.replace("mse", ""), "-e", working + mse, "-p", password]
        print(cmd)
        Popen(cmd).wait()
    except:
        pass

def get_dicom(mse):
    try:
        dicom = glob(working + "/{0}/E*".format(mse))[0]
        print("DICOM DIRECTORY:", dicom)
    except:
        run_dicom(mse)
        try:
            glob(working + "/{0}/E*".format(mse))[0]
            print(mse, "Successfully retrieved dicom from mspacman")
        except:
            print(mse, "Error retrieving dicom from mspacman, need to investigate further")
            with open(mspac_path + "/dicom.txt", "a") as text_file:
                text_file.write(mse + "\n")
            pass
        pass


def get_modality(mse):
    num = mse.split("mse")[-1]
    print("ms_dcm_exam_info", "-t", num, "-D")
    cmd = ["ms_dcm_exam_info", "-t", num, "-D"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    print("******These are the sequence names coming from the dicom images*****")
    for items in lines:
        print(items)
    print("********************************************************************")
    sequences  = ["T1", "T2", "FLAIR", "T1_Gad"]
    for sq in sequences:
        print("checking for...", sq)
        sequence_name = ""
        nii_type = sq
        if nii_type:
            try:
                sequence_name = filter_files(lines, nii_type, heuristic)[0]
                print(sequence_name, " is the {0}".format(sq))
            except:
                print(mse, "No {0} in dicom identified by the heuristic...Please check sequnces and heuristic".format(sq))
                pass
        if len(sequence_name) > 1:
            print("checking for sequence names in nifti and align folders")
            check_for_sq_names(mse, sq, "/nii/", sequence_name)
            check_for_sq_names(mse, sq, "/alignment/", sequence_name)
    get_nifti(mse)
    get_align(mse)



def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output


def run_nifti(mse):
    try:
        cmd = ["pbr", mse, "-w", "nifti", "-R"]
        print(cmd)
        Popen(cmd).wait()
    except:
        pass


def run_align(mse):
    try:
        cmd = ["pbr", mse, "-w", "align", "-R"]
        print(cmd)
        Popen(cmd).wait()
    except:
        pass


def check_in_nii_align(sq, x, mse, data, pipeline, sequence_name):
    if not sequence_name.startswith("ms"):
        check_nondeid(mse)
    if pipeline == "/nii/":

        if str(sequence_name) not in str(data[x]):
            print("No {0} in nifti status file, but {1} in dicom heuristic... re-running nifti conversion".format(sequence_name, sq))
            run_nifti(mse)
        else:
            print("THE {0} FILE EXISTS... ready to run align".format(sq))

        if "_reorient" in str(data[x]):
            run_nifti(mse)

    if pipeline == "/alignment/":
        if str(sequence_name) not in str(data[x]):
            print("No {0} in align status file, but {1} in dicom heuristic... re-running alignment".format(sequence_name, sq))
            run_align(mse)
        else:
            print("THE {0} FILE EXISTS...".format(sq))

        if "_reorient" in str(data[x]):
            run_align(mse)




def check_for_sq_names(mse, sq, pipeline, sequence_name ):
    nifti_align = pbr_dir(mse) +  pipeline + "/status.json"
    if os.path.exists(nifti_align):
        with open(nifti_align) as data_file:
            data = json.load(data_file)
            if sq == "T1":
                check_in_nii_align(sq, "t1_files", mse, data, pipeline, sequence_name)
            if sq == "T2":
                check_in_nii_align(sq, "t2_files", mse, data, pipeline, sequence_name)
            if sq == "FLAIR":
                check_in_nii_align(sq, "flair_files", mse, data, pipeline, sequence_name)
            if sq == "T1_Gad":
                check_in_nii_align(sq, "gad_files", mse, data, pipeline, sequence_name)

def get_nifti(mse):
    nifti = pbr_dir(mse) + "/nii/status.json"
    if not os.path.exists(nifti):
        run_nifti(mse)
    else:
        print(mse, "NIFTI HAS BEEN SUCCESSFULLY RUN")
        #check_nondeid(mse)


def get_align(mse):
    align =pbr_dir(mse) +"/alignment/status.json"
    if not os.path.exists(align):
        print("ALIGN DIRECTORY DOES NOT EXIST")
        run_align(mse)
    else:
        print(mse, "ALIGN HAS BEEN SUCCESSFULLY RUN", align)

def write_dicom_log(mse):
    dicom = ""
    try:
        dicom = glob(working + "/{0}/E*".format(mse))[0]
        print(dicom)
    except:
        with open(mspac_path+ "/dicom.txt", "a") as text_file:
            text_file.write(mse + "\n")
            print("no dicom for ", mse, "---writing dicom log")
    return dicom

def check_nii_localheur(mse):
    if os.path.exists(pbr_dir(mse) + '/nii/heuristic.json'):
        print("removing subject heuristic....",pbr_dir(mse) + '/nii/heuristic.json' )
        os.remove(pbr_dir(mse)+ '/nii/heuristic.json')
        run_nifti(mse)


def check_nondeid(mse):
    with open(mspac_path + "/not_deidentified.txt", "a") as text_file:
        text_file.write(mse + "\n")


def pbr_dir(mse):
    pbr = _get_output(mse) + '/' + mse + '/'
    return pbr

def run_first(mse):
    first = _get_output(mse) + '/'+ mse + "/first_all"
    if not os.path.exists(first):
        cmd = ["pbr", mse, "-w", "first_all", "-R"]
        Popen(cmd).wait()

def check_pbr(mse):
    print("running...", mse)
    get_dicom(mse)
    write_dicom_log(mse)

    if len(write_dicom_log(mse)) > 1:

        check_nii_localheur(mse)
        get_modality(mse)

        if not os.path.exists(pbr_dir(mse) + "/nii/status.json"):
            with open(mspac_path + "/nifti.txt", "a") as text_file:
                text_file.write(mse + "\n")
        if not os.path.exists(pbr_dir(mse) + "/alignment/status.json"):
            with open(mspac_path + "/align.txt", "a") as text_file:
                text_file.write(mse + "\n")
    #run_first(mse)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for the dicom, nifti, align pipelines and run them given an mse')
    parser.add_argument('-i', help = 'The input is either the mseID or an text files containing mseIDs')
    parser.add_argument
    args = parser.parse_args()
    mse = args.i
    if mse.endswith(".txt"):
        with open(mse,'r') as f:
            timepoints = f.readlines()
            for mse in timepoints:
                mse = mse.replace("\n", "")
                print(mse)
                check_pbr(mse)
    elif mse.startswith("mse"):
        check_pbr(mse)
    else:
        print(mse, "This is not an appropriate argument")

