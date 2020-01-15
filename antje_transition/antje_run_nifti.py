
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import shutil

text_file = "/data/henry6/gina/scripts/mse_all.txt"
with open(text_file) as f:
    lines = f.readlines()
    for x in lines:
        mse = x.rstrip('\n')
        mse = "mse" + mse.replace("mse", "").lstrip("0")
        e = glob("/working/henry_temp/PBR/dicoms/{}/E*".format(mse))
        #print(e)
        if len(e)>0:
            e = e[0]
            #print(e)
            #if not os.path.exists(_get_output(mse) +'/' +mse +'/nii/'):
                #print(mse)
        else:
            print(mse)

        #print("python", "/data/henry6/gina/scripts/run_pbr_troubleshoot_errors.py", "-i", mse)
        """print("python", "/data/henry6/gina/scripts/grid_submit.py", "'{0} {1} {2} {3}'".\
              format("python", "/data/henry6/gina/scripts/run_pbr_troubleshoot_errors.py", "-i", mse))"""

