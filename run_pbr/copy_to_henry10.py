from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import shutil

siena_long11 = "/data/henry11/PBR_long/subjects/"
siena_long10 = "/data/henry10/PBR_long/subjects/"
for msid in os.listdir(siena_long11):
    if msid.startswith("ms"):
        #print(msid)
        for siena_long in os.listdir(siena_long11 + msid):
            if siena_long.startswith("mse"):
                #print(siena_long)
                if not os.path.exists(siena_long10 + msid + "/siena_optibet/" + siena_long.replace("to", "")):
                    print(siena_long11 + msid +'/' + siena_long, siena_long10 + msid + "/siena_optibet/" + siena_long.replace("to", ""))
                    shutil.copytree(siena_long11 + msid +'/' + siena_long, siena_long10 + msid + "/siena_optibet/" + siena_long.replace("to", ""))