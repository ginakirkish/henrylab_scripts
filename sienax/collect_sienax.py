from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os

base_dir = "/data/henry7/PBR/subjects"

password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_pbr_new.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "Scan Date",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID", "FLAIR FILE"])
spreadsheet.writeheader()


for mse in os.listdir(base_dir):
    if os.path.exists(base_dir + mse + "/sienax_flair/"):
        path = base_dir + mse + "/nii/"
    
        
        

        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        
        cmd = ["ms_get_patient_id", "--exam_id", mse.replace("mse", "")]
        proc = Popen(cmd, stdout=PIPE)
        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[7:8]]
        msid = (str(lines)).split("'")[5]
        
        
        
        

        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]
                print(line.split()[-1], msid, mse)
                row = {"msid": msid, "mseID": mse}
            
            list = os.listdir(base_dir + mse + "/sienax_flair/") # dir is your directory path
            number_files = len(list)
            if number_files > 30:
                

                report = os.path.join(base_dir, mse, "sienax_flair/report.sienax")
                with open(report, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
                    for line in lines:
                    
                    
                    
                        if line.startswith("VSCALING"):
                            row["vscale"] =  line.split()[1]
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

                lm = os.path.join(base_dir, mse, "sienax_flair/lesion_mask.nii.gz")
                img = nib.load(lm)
                data = img.get_data()
                row["lesion vol (u, mm3)"] = np.sum(data)
                
                if not os.path.exists(PBR_base_dir+"/"+mse+"/alignment/status.json"):
                    continue
    
                with open("/data/henry7/PBR/subjects/"+mse+"/alignment/status.json") as data_file:  
                    data = json.load(data_file)
                    if len(data["flair_files"]) == 0:
                        flair_file = "none"
                    else:
                        flair_file = data["flair_files"][-1]
                        flair_file = (flair_file.split('/')[-1])
                        row["FLAIR FILE"] = flair_file

            else:
                print(mse, msid, "less than 30 sienax files")

        spreadsheet.writerow(row)
writer.close()
