
from glob import glob
import pandas as pd
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from subprocess import check_output
from subprocess import Popen, PIPE
import shutil
import subprocess 
from subprocess import check_call




base_dir = "/data/henry6/OPERA/"
for subjects in os.listdir(base_dir):
    if subjects.startswith("ms"):
        #print(subjects)
        if os.path.isdir(base_dir + subjects) and not os.listdir(base_dir + subjects) == []:
            #print(subjects)
            for mse in os.listdir(base_dir + subjects):
                if mse.startswith("mse"):
                    #print(mse)
                    if not os.path.exists("/working/henry_temp/PBR/dicoms/" + mse):
                        password = "Rosie1313"
                        new_mse = mse.replace("mse", "")
                        try:
                            cmd = ['ms_dcm_qr', '-t', new_mse,'-e',"/working/henry_temp/PBR/dicoms/" + mse, '-p', password]
                            print(cmd)
                        #cmd = ["pbr", mse, "-w", "nifti", "align", "-R", "-ps", "Rosie1313"]
                            check_call(cmd)
                            Popen(cmd, stdout=PIPE)
                            Popen.wait()
                        except Exception:
                            pass
