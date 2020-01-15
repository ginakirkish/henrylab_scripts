import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json, uuid
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from subprocess import Popen, PIPE
import pandas as pd
import shutil





pbr = ["/data/henry7/PBR/subjects/", "/data/henry11/PBR/subjects/"]
for path in pbr:
    for mse in os.listdir(path):
        if mse.startswith("mse") and len(mse) < 9:
            #print(mse)
            #if mse == "mse3581":
            try:
                align = _get_output(mse)+"/"+mse+"/nii/"
                for scans in os.listdir(align):
                    if "reorient" in scans:
                        reorient = align + scans
                        print(reorient, reorient.replace("/nii/", "/alignment/baseline_mni/").replace(".nii", "_nii.nii"))
                        print(mse)
                        #shutil.move(reorient, reorient.replace("/nii/", "/alignment/baseline_mni/"))
                #cmd = ["pbr", mse, "-w","nifti", "align","-R" ]
                #Popen(cmd).wait()
            except:
                pass