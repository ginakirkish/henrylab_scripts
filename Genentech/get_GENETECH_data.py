
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil

password = getpass("mspacman password: ")

def get_modality(mse, sequence):
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    sequence_name = ""
    nii_type = sequence
    if nii_type:
        try:
            sequence_name = filter_files(lines, nii_type, heuristic)[0]
            print(sequence_name, "This is the {0}".format(sequence))
        except:
            pass
        return sequence_name

def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output

def get_dicom(mse):
    dicom = "/working/henry_temp/PBR/dicom/{}/E*".format(mse)
    if len(dicom) > 0:
        dicom = "True"
    else:
        dicom = "False"
    return dicom

def get_nifti(mse):
    nifti = _get_output(mse)+"/"+mse+"/nii/status.json"
    if not os.path.exists(nifti):
        nii = "False"
    else:
        nii = "True"
    return nii

def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if not os.path.exists(align):
        align = "False"
    else:
        align = "True"
    return align

def get_first(mse):
    try:
        first = glob("/{0}/{1}/first_all/*fast_firstseg*".format(_get_output(mse), mse))[0]
        first = "True"
    except:
        first = "False"
        pass
    return first

def calc_first(seg, num):
    num1 = num - .5
    num2 = num + .5
    cmd = ["fslstats",seg,"-l", "{}".format(num1), "-u","{}".format(num2), "-V"]
    proc = Popen(cmd, stdout=PIPE)
    area = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
    return(area)

def get_first_values(mse):
    L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS = '','','','','','','','','','','','','','',''
    if os.path.exists(_get_output(mse) +"/"+ mse + "/first_all/"):
        for files in os.listdir(_get_output(mse) + "/" +mse +"/first_all/"):
            if files.endswith("firstseg.nii.gz") or files.endswith("firstsegs.nii.gz"):
                print(files)
                seg = _get_output(mse) + "/" +mse +"/first_all/"+ files
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

    return [L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS]

def get_FS(msid,mse):
    try:
        fs = glob("/data/henry6/PBR/surfaces/*{0}*{1}*".format(msid,mse))[0]
        print(fs)
        fs = "True"
    except:
        fs = "False"
        pass
    return fs

def get_sienax(mse):
    sienax_label, sienax, VS, PG, VCSF, GM, WM, BV = "", "", "", "", "", "", "", ""
    sienax_fl = "/{0}/{1}/sienaxorig_flair/report.sienax".format(_get_output(mse),mse)
    sienax_t2 = "/{0}/{1}/sienaxorig_t2/report.sienax".format(_get_output(mse),mse)
    sienax_optibet = glob("/{0}/{1}/sienax_optibet/ms*/lesion_mask.nii.gz".format(_get_output(mse),mse))
    if len(sienax_optibet) >= 1:
        sienax = sienax_optibet[0].replace("lesion_mask.nii.gz", "report.sienax")
        if os.path.exists("/{0}/{1}/lesion_origspace_flair/".format(_get_output(mse),mse)):
            sienax_label = "sienaxorig_flair"
        else:
            sienax_label = "sienaxorig_t2"
    elif os.path.exists(sienax_fl):
        sienax_label = "sienaxorig_flair"
        sienax = sienax_fl
    elif os.path.exists(sienax_t2):
        sienax_label = "sienaxorig_t2"
        sienax = sienax_t2
    elif os.path.exists(sienax_fl.replace("sienaxorig","sienax")):
        sienax_label = "sienax_flair"
    elif os.path.exists(sienax_t2.replace("sienaxorig","sienax")):
        sienax_label = "sienax_t2"
    elif os.path.exists(sienax_t2.replace("sienaxorig", "sienax_optibet")):
        sienax_label = "sienax_optibet"
    else:
        try:
            sienax = glob("/{0}/{1}/sienax*/ms*/report.sienax".format(_get_output(mse),mse))[-1]
        except:
            sienax_label = "False"
            pass
    if os.path.exists(sienax):
        with open(sienax, "r") as f:
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
    return [sienax_label, sienax, VS, PG, VCSF, GM, WM, BV]



def get_siena_data(msid, mse, mse2):
    #siena_long = glob("/data/henry*/PBR_long/subjects/" + msid + '/siena_optibet/')
    henry12 = "/data/henry12/PBR_long/subjects/" + msid + '/siena_optibet/'
    henry10 = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
    pbvc_henry12, mse2_t1, siena_label, pbvc_henry10, final_pbvc = "", "", "", "",""
    try:
        align = "{}/{}/alignment/status.json".format(_get_output(mse2), mse2)
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    mse2_t1 = data["t1_files"][-1].split('/')[-1].split('-')[3].replace(".nii.gz", "")
                    if "DESPOT" in mse2_t1:
                        mse2_t1 = data["t1_files"][0]
                    print("MSE2", mse2_t1)
    except:
        pass
    if os.path.exists(henry12):
        for mse_siena12 in os.listdir(henry12):
            if mse_siena12.startswith(mse) and str(mse_siena12).endswith(str(mse2)):
                siena_report = os.path.join(henry12, mse_siena12, "report.siena")
                if os.path.exists(siena_report):
                    print(siena_report)
                    siena_label = "True"
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                pbvc_henry12 =  line.split()[1]


    if os.path.exists(henry10):
        for mse_siena in os.listdir(henry10):
            if mse_siena.startswith(mse) and str(mse_siena).endswith(str(mse2)):
                siena_report = os.path.join(henry10, mse_siena, "report.siena")
                if os.path.exists(siena_report):
                    print(siena_report)
                    siena_label = "True"
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                pbvc_henry10 =  line.split()[1]
                                siena_path = henry10 + mse_siena

    if len(pbvc_henry10) >4 and len(pbvc_henry12) > 4:
        if pbvc_henry10 > pbvc_henry12:
            final_pbvc = pbvc_henry12
            print(mse,mse2)
            print( pbvc_henry10, "this is larger than...",  pbvc_henry12)
            print("removing.....", siena_path)
            shutil.rmtree(siena_path)
        else:
            final_pbvc = pbvc_henry10
    elif len(pbvc_henry12) > 4:
        final_pbvc = pbvc_henry12
    elif len(pbvc_henry10) > 4:
        final_pbvc = pbvc_henry10
    else:
        final_pbvc = ""

    return [final_pbvc, mse2_t1, siena_label]

def get_scanner_info(mse, x):
    info = ""
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        for line in output:
            if x in line:
                dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                info = dicom_info
    except:
        pass
    return info

def sienax_long(msid, mse):
    pbr_long = "/data/henry10/PBR_long/subjects/"
    if not os.path.exists(pbr_long + msid + "/lst_edit_sienax/"):
        lst_long = False
    else:
        lst_long = True
    return lst_long

def get_lst(mse):
    lst = ""
    try:
        lst = glob(_get_output(mse)+"/"+mse+"/mindcontrol/ms*/lst/lst_edits/no_FP_filled_*")[0]
    except:
        pass
    if len(lst) > 3:
        lst = "LST - FINISHED"
    elif os.path.exists(_get_output(mse)+"/"+mse+ "/lst/lpa"):
        lst = "lst - not edited"
    else:
        lst = "none"
    return lst

def check_for_resampling_sienax(mse):
    check = ""
    try:
        t1 = glob("{}/{}/sienaxorig_*/I_brain.nii.gz".format(_get_output(mse), mse ))[-1]
        cmd = ["fslstats", t1, "-R" ]
        proc = Popen(cmd, stdout=PIPE)
        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
        check = ""
        if max.endswith(".0"):
            check = True
        else:
            check = False
    except:
        pass
    return check


def check_for_resampling_align(mse):
        check = ""
        align = _get_output(mse)+"/"+mse+"/alignment/status.json"
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1]
                    try:
                        cmd = ["fslstats", t1_file, "-R" ]
                        proc = Popen(cmd, stdout=PIPE)
                        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
                        check = ""
                        if max.endswith(".0"):
                            check = True
                        else:
                            check = False
                    except:
                        pass
                    return check

def check_for_resampling_siena(msid, mse):
    check = True
    siena_check = "/data/henry6/gina/siena_check/"
    pbr = ["/data/henry10/PBR_long/subjects", "/data/henry12/PBR_long/subjects"]
    for pbr_long in pbr:
        siena = glob("{}/{}/siena_optibet/{}_*".format(pbr_long, msid, mse))
        if len(siena) > 0:
            print(siena)
            siena = siena[0]
            for items in siena:
                A_file = items + "/A.nii.gz"
                B_file = items + "/B.nii.gz"
                if os.path.exists(A_file) and os.path.exists(B_file):

                    shutil.copyfile(A_file, siena_check + mse + ".nii.gz")
                    shutil.copyfile(B_file, siena_check + mse + ".nii.gz")
                    A_check = str(check_for_resampling_align(A_file.replace(".nii","_new.nii")))
                    B_check = str(check_for_resampling_align(B_file.replace(".nii", "_new.nii")))
                    if A_check == "False" or B_check == "False":
                        check = False
    return(check)




def get_msid(mse):
    cmd = ["ms_get_patient_id", "--exam_id", mse.split("mse")[1]]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][-1][2].split("'")[-1]
    return output

def get_date(mse):
    import subprocess
    date = ""
    proc = subprocess.Popen(["ms_get_phi", "--examID", mse, "-p",password],stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = str(line.rstrip())
        if "StudyDate" in   line:
            date=   line.split()[-1].lstrip("b'").rstrip("'")
            print("Date", date)
    return date

def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
        date = str(df.loc[idx, 'date']).split(".0")[0].replace("-","")
        #mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
        mse = df.loc[idx, 'mse']
        mse2 = ""
        mse3 = ""
        if not str(mse) == "nan":
            mse = "mse" + mse
            print(mse)
            if "_" in mse:
                #mse = "mse" + mse.split('_')[0]
                mse2 = "mse"+ str(mse).split('_')[1]
                print(mse2)
                mse1 = str(mse).split('_')[0]
                try:
                    mse3 = "mse"+ str(mse).split('_')[3]
                    print(mse3)
                except:
                    pass
                mse = mse1



            if len(msid) < 3:
                msid = get_msid(mse)
            if len(date) < 3:
                date = get_date(mse)
            df.loc[idx, "msid"] = msid
            df.loc[idx, "mse1"] = mse
            df.loc[idx, "mse2"] = mse2
            df.loc[idx, "mse3"] = mse3
            df.loc[idx, "date"] = date

            #df.loc[idx, 'T1'] = get_modality(mse, "T1")
            #df.loc[idx, "Software"] = get_scanner_info(mse, "SoftwareVersions")
            #df.loc[idx, "Scanner"] = get_scanner_info(mse, "StationName")

            #sienax
            SX = get_sienax(mse)
            df.loc[idx, "lst check"] = get_lst(mse)
            df.loc[idx, "sienax_long"] = sienax_long(msid, mse)
            df.loc[idx, "resample sienax"] = check_for_resampling_sienax(mse)
            df.loc[idx, 'sienax'] = SX[0]
            df.loc[idx, 'V Scale'] = SX[2]
            df.loc[idx, 'pGM'] = SX[3]
            df.loc[idx, 'CSF'] = SX[4]
            df.loc[idx, 'GM'] = SX[5]
            df.loc[idx, 'WM'] = SX[6]
            df.loc[idx, "BV"] = SX[7]
            if len(mse2) > 3:
                SX = get_sienax(mse)
                df.loc[idx, "lst check - mse2"] = get_lst(mse2)
                df.loc[idx, "sienax_long - mse2"] = sienax_long(msid, mse2)
                df.loc[idx, "resample sienax - mse2"] = check_for_resampling_sienax(mse2)
                df.loc[idx, 'sienax - mse2'] = SX[0]
                df.loc[idx, 'V Scale - mse2'] = SX[2]
                df.loc[idx, 'pGM - mse2'] = SX[3]
                df.loc[idx, 'CSF - mse2'] = SX[4]
                df.loc[idx, 'GM - mse2'] = SX[5]
                df.loc[idx, 'WM - mse2'] = SX[6]
                df.loc[idx, "BV - mse2"] = SX[7]
            if len(mse3) > 3:
                SX = get_sienax(mse)
                df.loc[idx, "lst check - mse3"] = get_lst(mse2)
                df.loc[idx, "sienax_long - mse3"] = sienax_long(msid, mse2)
                df.loc[idx, "resample sienax - mse3"] = check_for_resampling_sienax(mse2)
                df.loc[idx, 'sienax - mse3'] = SX[0]
                df.loc[idx, 'V Scale - mse3'] = SX[2]
                df.loc[idx, 'pGM - mse3'] = SX[3]
                df.loc[idx, 'CSF - mse3'] = SX[4]
                df.loc[idx, 'GM - mse3'] = SX[5]
                df.loc[idx, 'WM - mse3'] = SX[6]
                df.loc[idx, "BV - mse3"] = SX[7]

    df.to_csv(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)







"""

 elif os.path.exists("/{0}/{1}/sienax_flair/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 MNI space - flair MM lesions"
    elif os.path.exists("/{0}/{1}/sienax_flair/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 MNI space - t2 MM lesions"
    elif os.path.exists("/{0}/{1}/sienax_lst/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - lst lesions"
    elif os.path.exists("/{0}/{1}/sienaxorig_t1manseg/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - man les seg"
    elif os.path.exists("/{0}/{1}/sienaxorig_t1recon/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - t1 recon les"
    elif os.path.exists("/{0}/{1}/sienax_t1recon/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 MNI space - recon les seg"
    elif os.path.exists("/{0}/{1}/sienaxorig_t1recon/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - t1 recon les"
    elif os.path.exists("/{0}/{1}/sienax_t1_les/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 les"
    elif os.path.exists("/{0}/{1}/sienaxorig_noles/report.html".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - no les"
    elif os.path.exists("/{0}/{1}/sienax_optibet/status.json".format(_get_output(mse),mse)):
        sienax = "sienax T1 orig space - no les"

df.loc[idx, 'siena'] = get_siena(msid, mse)
"""
