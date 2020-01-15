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
from subprocess import Popen, PIPE


df = pd.read_csv("/home/sf522915/Documents/EPIC1_Oct13_calibrated.csv")


df.columns.values[1:62]

for idx in range(len(df)):
    mse = df.loc[idx, 'mse']
    timepoint = df.loc[idx, 'VisitType']
    if "Baseline" in timepoint:
        #print(mse, timepoint)
        if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
            with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                data = json.load(data_file)

                if len(data["t1_files"]) == 0:
                    t1_file = "none"
                    #print(mse, "NO T1 file")


                else:
                    t1_file = data["t1_files"][-1]
                    bl_t1_mni = _get_output(mse)+'/'+mse +"/alignment/baseline_mni/"+os.path.split(t1_file)[-1].replace(".nii.gz", "_T1mni.nii.gz").replace("_reorient", "")
                    out_t1 = bl_t1_mni.replace(".nii", "_nnreg.nii")

                    #lesion = _get_output(mse) + '/' + mse + "/lesion_mni/lesion_final_new.nii.gz"
                    sienax = _get_output(mse) + '/' + mse + '/sienax_t2_bl/'
                    if os.path.exists(sienax):
                        if not os.path.exists(sienax + "/lesion_mask.nii.gz"):
                            try:
                                lesion = glob(_get_output(mse) + '/' + mse + "/lesion_mni*/lesion_final*.nii.gz")[0]
                                print(mse)
                                #print(lesion)
                                #cmd = ["sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/']
                                print("sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/')
                                #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py", "{4}sienax_optibet {0} -lm {1} -r -d -o {2}/{3}/sienax_t2_bl{4}".format(out_t1,lesion,_get_output(mse),mse,'"') ]
                                #print("python", "/data/henry6/gina/scripts/grid_submit.py", "{4}sienax_optibet {0} -lm {1} -r -d -o {2}/{3}/sienax_t2_bl{4}".format(out_t1,lesion,_get_output(mse),mse,'"') )
                                #Popen(cmd).wait()
                            except:
                                pass
                    #cmd = ["fslstats", _get_output(mse) + '/' + mse + '/sienax_t2_bl/lesion_mask.nii.gz', "-M" ]'
                    #proc = Popen(cmd, stdout=PIPE)
                    #output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    #output = output[0]
                    #print(output)

                    #if not os.path.exists(_get_output(mse) + '/' + mse + '/sienax_t2_bl/report.html'):

                    #if not os.path.exists(out_t1) :
		            #os.mkdir(_get_output(mse) + '/' + mse + '/sienax_t2_bl/')
                    #cmd = ["flirt", "-interp", "nearestneighbour", '-dof', "6", "-in", t1_file, "-ref", bl_t1_mni, "-out", out_t1 ]
                    #print("flirt", "-interp", "nearestneighbour","-dof", "6", "-in", t1_file, "-ref", bl_t1_mni, "-out", out_t1)
                    #Popen(cmd).wait()
                        #lesion = _get_output(mse) + '/' + mse + "/lesion_mni/lesion_final_new.nii.gz"
                        #cmd = ["sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/']
                        #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py", '"',"sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/','"']
                    #print("sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/')
                        #print("python", "/data/henry6/gina/scripts/grid_submit.py",'"',"sienax_optibet", out_t1, "-lm", lesion, "-r", "-d", "-o",_get_output(mse) + '/' + mse + '/sienax_t2_bl/','"')
                        #Popen(cmd).wait()

