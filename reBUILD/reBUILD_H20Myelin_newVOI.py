import nibabel as nib
import numpy as np
from glob import glob
import os
import csv
from subprocess import Popen, PIPE
import nibabel as nibabel


root_dir = '/data/henry1/study_reBUILD/MNI_WM_analysis/'
base_dir = root_dir + "/VOIs/"
nawm_dir = base_dir + "/nawm/"
lesion_dir = base_dir + "/lesions/"
long_voi = base_dir + "longitudinal/"
splenium = long_voi + "/Splenium_CC.nii.gz"
CST_intcap = long_voi + "CST_Int-Cap.nii.gz"


VOI = [splenium, CST_intcap]

"""
for subjects in os.listdir(nawm_dir):
    for voi in VOI:
        new_voi = subjects.split('.')[0]+"_"+ voi.split('/')[-1]
        print(new_voi)
        cmd = ["fslmaths", nawm_dir + subjects, "-mul", voi, base_dir + "/nawm_VOI/" + new_voi]
        proc = Popen(cmd)
        proc.wait()
        print(cmd)

for nawm_VOI in os.listdir(base_dir + "/nawm_VOI/"):
    if "Splenium" in nawm_VOI: 
        print(nawm_VOI)
        msid = nawm_VOI.split("-")[0]
        mse = nawm_VOI.split("-")[1]
        subject = msid + "-" + mse
        for h20 in os.listdir(root_dir + "/Neeb"): 
            if h20.startswith(subject): 
                #print(h20, nawm_VOI)
                splenium_new = h20.split(".")[0] + "_nawm_Splenium_CC.nii.gz" 
                cmd = ["fslmaths",root_dir + "/Neeb/" + h20, "-mul", base_dir + "/nawm_VOI/" + nawm_VOI, base_dir +"/Neeb_Splenium_nawm/"+ splenium_new  ]
                print(cmd)
                proc = Popen(cmd)
                proc.wait()

            
        #print(msid,mse)

for nawm_VOI in os.listdir(base_dir + "/nawm_VOI/"):
    msid = nawm_VOI.split("-")[0]
    if "Splenium" in nawm_VOI:
    #print(msid)
        for Neeb in os.listdir(root_dir + "/Neeb/"):
            if Neeb.startswith(msid):
                mse = Neeb.split("-")[1]
                print(msid, nawm_VOI, Neeb, mse)
                final_file = msid + "-" + mse +"_"+ nawm_VOI.split("-")[2].replace(".nii.gz", "") +"_" + Neeb.split("-")[2]
                print(final_file)
                cmd = ["fslmaths", base_dir + "/nawm_VOI/" + nawm_VOI, "-mul",root_dir + "/Neeb/"+ Neeb, base_dir + "/Neeb_Splenium_nawm/" + final_file]
                proc = Popen(cmd)
                proc.wait()
                print(cmd)

for nawm_VOI in os.listdir(base_dir + "/nawm_VOI/"):
    msid = nawm_VOI.split("-")[0]
    if "CST_Int-Cap" in nawm_VOI:
    #print(msid)
        for Neeb in os.listdir(root_dir + "/Neeb/"):
            if Neeb.startswith(msid):
                mse = Neeb.split("-")[1]
                print(msid, nawm_VOI, Neeb, mse)
                final_file = msid + "-" + mse +"_"+ nawm_VOI.split("-")[2].replace(".nii.gz", "") +"_" + Neeb.split("-")[2]
                print(final_file)
                cmd = ["fslmaths", base_dir + "/nawm_VOI/" + nawm_VOI, "-mul",root_dir + "/Neeb/"+ Neeb, base_dir + "/Neeb_CST_intcap_nawm/" + final_file]
                proc = Popen(cmd)
                proc.wait()
                print(cmd)




for neeb in os.listdir(root_dir + "/Neeb/" ):
    cmd = ["fslmaths",base_dir + , root_dir + "/Neeb/" + neeb, "-mul", base_dir + "/Neeb_Splenium_nawm/"+ neeb.replace(".nii.gz", "_nawm_splenium.nii.gz")]
    print(cmd)
    proc = Popen(cmd)
    proc.wait()

for neeb in os.listdir(root_dir + "/Neeb/" ):
    cmd = ["fslmaths", root_dir + "/Neeb/" + neeb, "-mul", CST_intcap, base_dir + "/Neeb_CST_intcap/"+ neeb.replace(".nii.gz", "_cst_intcap.nii.gz")]
    print(cmd)
    proc = Popen(cmd)
    proc.wait()"""

writer = open(base_dir + "median_VOI_Neeb_splenium_namw.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "mse", "VOI", "Map", "median"])
spreadsheet.writeheader()


for scan in os.listdir(base_dir + "/Neeb_Splenium_nawm/"):
    cmd = ["fslstats", base_dir + "/Neeb_Splenium_nawm/" + scan, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    median = float(output[0])
    print(median, scan)

    
    row = {}
    
    row["msid"] =  scan.split('-')[0]
    row['mse'] = scan.split('-')[1].split("_")[0]
    
    #row['VOI'] = scan.split("_")[1] 
    row["median"] = median


    if "H2O" in scan:
        row["Map"] = "H20"
    if "Myelin" in scan:
        row["Map"] = "Myelin"

    
    
    row["VOI"] = "Splenium_nawm"

    spreadsheet.writerow(row)
writer.close()




writer = open(base_dir + "median_VOI_Neeb_CST_intcap_nawm.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "mse", "VOI", "Map", "median"])
spreadsheet.writeheader()


for scan in os.listdir(base_dir + "/Neeb_CST_intcap_nawm/"):
    cmd = ["fslstats", base_dir + "/Neeb_CST_intcap_nawm/" + scan, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    output = output[0]
    median = float(output[0])
    print(median, scan)

    
    row = {}
    
    row["msid"] =  scan.split('-')[0]
    row['mse'] = scan.split('-')[1].split("_")[0]
    
    #row['VOI'] = scan.split("_")[1] 
    row["median"] = median


    if "H2O" in scan:
        row["Map"] = "H20"
    if "Myelin" in scan:
        row["Map"] = "Myelin"

    row["VOI"] = "CST_intcap_nawm"

    spreadsheet.writerow(row)
writer.close()

