import os
from glob import glob
from subprocess import Popen, PIPE
import json
from nipype.interfaces import fsl
import argparse
import shutil
import numpy as np
import math
import pandas as pd
import numpy as np
import scipy.ndimage as ndi
import sys
from scipy.ndimage.measurements import label
import csv

from subprocess import call
import nibabel as nib
import collections


df = pd.read_csv("/home/sf522915/EPIC1_imaging_exams_brainspine.csv")

PBR_base_dir = "/data/henry7/PBR/subjects/"
for _, row in df.iterrows():
    mse = row['mseID']
    mse = str(mse)
    mse ="mse" + mse.replace("mse", "").lstrip("0")
    if os.path.exists(PBR_base_dir + mse + "/lesion_mni/lesion_labeled.nii.gz"):
        lesion = PBR_base_dir + mse + "/lesion_mni/lesion_labeled.nii.gz"        
        lesion_img = nib.load(lesion)
        lesion_data = lesion_img.get_data()
        lesion_affine = lesion_img.get_affine
        lesion_data = np.array(lesion_data)
        print(lesion_data)
