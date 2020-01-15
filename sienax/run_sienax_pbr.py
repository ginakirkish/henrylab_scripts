
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil
import nibabel as nib
import numpy as np

sienax_old = glob("/data/henry*/PBR/subjects/mse*/sienaxorig_*/")
if len(sienax_old) > 0:
    for sienax in sienax_old:
    #sienax_old = sienax_old[-1]
        print(sienax)
        mse = sienax.split("/")[5]
        print(mse)
        if not os.path.exists("{}/{}/sienax_optibet/".format(_get_output(mse), mse)):
            cmd = ["pbr", mse, "-w", "sienax_optibet", "-R"]
            Popen(cmd).wait()
        sienax_new = glob("{}/{}/sienax_optibet/ms*/report.sienax".format(_get_output(mse), mse))
        if len(sienax_new) > 0:
            print("removing....", sienax)
            shutil.rmtree(sienax)


