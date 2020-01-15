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
import shutil
df = pd.read_csv("/home/sf522915/Documents/EPIC_not_done_regles.csv")


df.columns.values[1:62]

for idx in range(len(df)):
    mse = df.loc[idx, 'mse']
    msid = df.loc[idx, 'msid']
    timepoint = df.loc[idx, 'VisitType']
    if "Baseline" in timepoint:
        orig_sienax = "/data/henry6/alyssa/no_lesions_sienax/baseline/{0}/I_brain.nii.gz".format(msid)

        orig_les = "/data/henry6/alyssa/lesions_reg/manual_lesions/baseline/{0}_baseline_lesions.nii.gz".format(msid)
        mat = _get_output(mse) +'/' + mse+ "/sienax/omat.mat"
        #print(orig_sienax, pbr_sienax, mat)
        if os.path.exists(orig_sienax):
            try:
                pbr_sienax = glob("/data/henry*/PBR/subjects/{0}/sienax/I_brain.nii.gz".format(mse))[0]
                #print(pbr_sienax, mse)
                #cmd = ["flirt", "-dof", "6", "-in", orig_sienax, "-ref", pbr_sienax, "-omat",mat , "-out", pbr_sienax.split('/')[-1] + "I_brain_new.nii.gz"]
                #print(cmd)
                #Popen(cmd).wait()
                cmd = ["flirt", "-init", mat, "-applyxfm", "-in",orig_les, "-ref", pbr_sienax, "-out", _get_output(mse) +'/' +mse +'/lesion_mask.nii.gz']
                #Popen(cmd).wait()
                #print(cmd)


            except:
                print(mse)
                pass
            msid ="ms" + msid.replace("ms","").lstrip("0")
            long = "/data/henry10/PBR_long/subjects/" +msid

            if not os.path.exists(long):
                os.mkdir(long)
            if not os.path.exists(long +'/MNI/'):
                os.mkdir(long +'/MNI/')
                print(long +'/MNI/')
                #continue

            if os.path.exists(_get_output(mse) +'/' +mse):
                with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                    data = json.load(data_file)
                    if len(data["t1_files"]) > 0:
                        t1_file = _get_output(mse) +'/' +mse +'/alignment/baseline_mni/'+ data["t1_files"][-1].split("/")[-1].replace(".nii","_T1mni.nii")
                        #print(t1_file)
                    if len(data["t2_files"]) > 0:
                        t2_file = _get_output(mse) +'/' +mse +'/alignment/baseline_mni/'+ data["t2_files"][-1].split("/")[-1].replace(".nii","_T1mni.nii")
                        #print(t2_file)
                        print(t2_file, long +'/MNI/' + t2_file.split('/')[-1])
                        shutil.copyfile(t2_file, long +'/MNI/' + t2_file.split('/')[-1])
                    if len(data["flair_files"]) > 0:
                        flair_file = _get_output(mse) +'/' +mse +'/alignment/baseline_mni/'+ data["flair_files"][-1].split("/")[-1].replace(".nii","_T1mni.nii")
                        print(flair_file, long +'/MNI/' + flair_file.split('/')[-1])
                        shutil.copyfile(flair_file, long +'/MNI/' + flair_file.split('/')[-1])
                cmd = ["sienax_optibet", t1_file, "-lm",  _get_output(mse) +'/' +mse +'/lesion_mask.nii.gz', "-r", "-d", "-o", _get_output(mse)+'/'+mse+'/sienax_t1_les' ]
                #Popen(cmd).wait()
                #print("sienax_optibet", t1_file, "-lm",  _get_output(mse) +'/' +mse +'/lesion_mask.nii.gz', "-r", "-d", "-o", _get_output(mse)+'/'+mse+'/sienax_t1_les' )
                sienaxt1 = _get_output(mse)+'/'+mse+'/sienax_t1_les/'
                wm = (sienaxt1 +'/I_stdmaskbrain_pve_2.nii.gz', long + '/wm_'+mse +".nii.gz" )
                gm = (sienaxt1 +'/I_stdmaskbrain_pve_1.nii.gz', long + '/gm_'+mse +".nii.gz" )
                lesion = (sienaxt1 +'/lesion_mask.nii.gz', long + '/lesion_'+mse +".nii.gz" )
                shutil.copyfile(sienaxt1 +'/I_stdmaskbrain_pve_2.nii.gz', long + '/MNI/wm_'+mse +".nii.gz")
                shutil.copyfile(sienaxt1 +'/I_stdmaskbrain_pve_1.nii.gz', long + '/MNI/gm_'+mse +".nii.gz")
                shutil.copyfile(sienaxt1 +'/lesion_mask.nii.gz', long + '/MNI/lesion_'+mse +".nii.gz")






