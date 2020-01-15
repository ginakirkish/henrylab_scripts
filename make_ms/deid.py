from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import shutil
from subprocess import check_call
import subprocess
import os

def get_t1(mse):
    t1_file = "ms"
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1]
    return t1_file

def get_msid(mse):
    cmd = ["ms_get_patient_id", "--exam_id", mse.split("mse")[1]]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][-1][2].split("'")[-1]
    return output

def deid(msid, mse):
    work = glob("/working/henry_temp/PBR/dicoms/{}/E*/".format(mse))
    if len(work)>0:
        
        cmd = ["dcm_deid", "-e", work[-1],"--patID",msid,"--studyID", mse]
        print("dcm_deid", "-e", work[-1],"--patID",msid,"--studyID", mse)
        Popen(cmd).wait()
        mse_num = mse.replace("mse","")
        if int(mse_num)>4500:
            cmd = ["pbr",mse,"-w", "nifti", "align", "-R"]
            #Popen(cmd).wait()

def rename(msid, mse,pbr, t1 ):
    for dirt in os.listdir(pbr):
        for files in os.listdir(pbr + '/'+ dirt):
            msid_bad = t1.split("-")[0]
            mse_bad = t1.split("-")[1]
            if files.startswith(msid_bad):
                old = pbr + '/' + dirt + '/'+files 
                new =  pbr + '/' + dirt + '/'+files.replace(msid_bad, msid).replace(mse_bad, mse)
                os.rename(old, new)
                print("****************")
                print(old, new )
            
            
        

henry = ["henry7","henry11"]
for h in henry:
    for mse in os.listdir("/data/"+ h+ "/PBR/subjects/"):
        pbr = "/data/"+ h+ "/PBR/subjects/" + mse
        if mse.startswith("mse") and os.path.exists(pbr + "/alignment/"):
            try:
                t1 = get_t1(mse)
                #print(mse, t1)
                t1 = t1.split('/')[-1]
                if not t1.startswith("ms"):
                    print(mse, t1)
                    msid = get_msid(mse)
                    deid(msid, mse)
                    rename(msid, mse, pbr, t1)
            except:
                pass
