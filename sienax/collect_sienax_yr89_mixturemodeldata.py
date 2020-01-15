from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
from subprocess import Popen, Popen, PIPE
import json
from nipype.interfaces import fsl
import argparse
import shutil
import pandas as pd
import pbr
from pbr.base import _get_output



password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_yr89_mixturemodelFINAL.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid","mseID", "Scan Date", "flair file","t2 file", "t1 file", "scanner", "sienax",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)" ])
spreadsheet.writeheader()



for mse in os.listdir("/data/henry7/PBR/subjects/"):
    row = {}
    if not mse.startswith("mse") and not mse.endswith("B"):
        continue
    
#mse_list = ["mse3169", "mse3139", "mse3127", "mse3162", "mse3143", "mse3149", "mse3170", "mse1358", "mse4530", "mse396", "mse3165"]
#for mse in mse_list: 
    print(mse)
    if os.path.exists(_get_output(mse)+'/' + mse + "/sienax_flair/"):
        #print(_get_output(mse) +'/'+ mse + "/sienax_flair/")
        path = _get_output(mse)+'/' + mse + "/nii/"
    
        
     
        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        cmd = ["ms_get_patient_id", "--exam_id", mse.replace("mse", "")]
        proc = Popen(cmd, stdout=PIPE)
        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[7:8]]
        try: 
            msid = (str(lines)).split("'")[5]
            #print(msid)
            row = {"msid": msid, "mseID": mse, "sienax": "FLAIR"}
            #print(row)
        except:
            pass
        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]
                #print(line.split()[-1], msid, mse)
            
            list = os.listdir(_get_output(mse) +'/'+ mse + "/sienax_flair/") # dir is your directory path
            number_files = len(list)
            if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
                continue
    
            with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:  
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file = "none"
                row["t1 file"] = t1_file
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1])
                #print(t1_file)
                row["t1 file"] = t1_file

            if len(data["flair_files"]) == 0:
                flair_file = "none"
                row["flair file"] = flair_file
            else:
                flair_file = data["flair_files"][-1]
                flair_file = (flair_file.split('/')[-1])
                #print(flair_file)
                row["flair file"] = flair_file
        try: 

            series = t1_file.split("-")[2].lstrip("0")
            #print(series)
            if not len(series) > 0:
                series = "1"
            dcm = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))         
            if len(dcm) > 0 :
                dcm = dcm[0]
                #print(dcm)
                cmd = ["dcmdump", dcm]
                proc = Popen(cmd, stdout=PIPE)
                lines = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
                row["scanner"] = lines
                if "qb3-3t" in lines:
                    #print("qb3-3t")
                    row["scanner"] = "qb3"
                elif "SIEMENS" in lines:
                    #print("SIEMENS")
                    row["scanner"] = "Skyra"
                elif "CB3TMR"  or "CB-3TMR" in lines:
                    print("CB3TMR")
                    row["scanner"] = "CB"
                else:
                    row["scanner"] = "unknown"
        except: 
            pass 
        if number_files > 30:
                

            report = os.path.join(_get_output(mse), mse, "sienax_flair/report.sienax")
            with open(report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                      
                    if line.startswith("VSCALING"):
                        row["vscale"] =  line.split()[1]
                        print("...its working")
                    elif line.startswith("pgrey"):
                        row["cortical vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("vcsf"):
                        row["vCSF vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("GREY"):
                        row["GM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("WHITE"):
                        row["WM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("BRAIN"):
                        row["brain vol (u, mm3)"] = line.split()[2]

            lm = os.path.join(_get_output(mse), mse, "sienax_flair/lesion_mask.nii.gz")
            img = nib.load(lm)
            data = img.get_data()
            row["lesion vol (u, mm3)"] = np.sum(data)
                
                
        else:
            print(mse, msid, "less than 30 sienax files")
    

    elif os.path.exists(_get_output(mse)+'/' + mse + "/sienax_t2/"):
        #print(_get_output(mse) +'/'+ mse + "/sienax_t2/")
        path = _get_output(mse)+'/' + mse + "/nii/"
    
        
     
        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        
        cmd = ["ms_get_patient_id", "--exam_id", mse.replace("mse", "")]
        proc = Popen(cmd, stdout=PIPE)
        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[7:8]]
        try: 
            msid = (str(lines)).split("'")[5]
        
            row = {"msid": msid} 
        except:
            pass 
        row = {"mseID": mse, "sienax": "t2" }


        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]
                #print(line.split()[-1], msid, mse)
            
            list = os.listdir(_get_output(mse)+ '/' + mse + "/sienax_t2/") # dir is your directory path
            number_files = len(list)
            if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
                continue
    
            with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:  
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file = "none"
                row["t1 file"] = t1_file
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1])
                #print(t1_file)
                row["t1 file"] = t1_file

            if len(data["t2_files"]) == 0:
                t2_file = "none"
                row["t2 file"] = t2_file
            else:
                t2_file = data["t2_files"][-1]
                t2_file = (t2_file.split('/')[-1])
                row["t2 file"] = t2_file

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
                #print("qb3-3t")
                row["scanner"] = "qb3"
            elif "SIEMENS" in lines:
                #print("SIEMENS")
                row["scanner"] = "Skyra"
            elif "CB3TMR"  or "CB-3TMR" in lines:
                #print("CB3TMR")
                row["scanner"] = "CB"
            else:
                row["scanner"] = "unknown"
        if number_files > 30:
            report = os.path.join(_get_output(mse), mse, "sienax_t2/report.sienax")
            with open(report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                    
                    
                    
                    if line.startswith("VSCALING"):
                        row["vscale"] =  line.split()[1]
                        print("...its working")
                    elif line.startswith("pgrey"):
                        row["cortical vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("vcsf"):
                        row["vCSF vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("GREY"):
                        row["GM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("WHITE"):
                        row["WM vol (u, mm3)"] = line.split()[2]
                    elif line.startswith("BRAIN"):
                        row["brain vol (u, mm3)"] = line.split()[2]

            lm = os.path.join(_get_output(mse), mse, "sienax_t2/lesion_mask.nii.gz")
            img = nib.load(lm)
            data = img.get_data()
            row["lesion vol (u, mm3)"] = np.sum(data)
                
                
        else:
            print(mse, "less than 30 sienax files")


    spreadsheet.writerow(row)

writer.close()
