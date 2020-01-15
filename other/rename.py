
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
from subprocess import Popen
import json


dir = "/data/henry11/PBR/subjects/mse12673/nii/"

for name in os.listdir(dir):
    if name.endswith(".nii.gz"):
        print(name)
        ms = name.split("-")[0]
        mse = name.split("-")[1]
        new_name = name.replace(ms, "ms2205").replace(mse, "mse12673")
        print(new_name)
        status = dir + "/status.json"
        os.rename(dir + name,dir +  new_name)
        print(status)

        with open(status) as data_file:
            data = json.load(data_file)
            data = str(data)
            #print(data)
            new_data = data.replace(ms, "ms2205").replace(mse, "mse12673")
            #new_json = json.load(status)
            print(new_data)




