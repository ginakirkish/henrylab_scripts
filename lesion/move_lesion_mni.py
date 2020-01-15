
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

base = "/data/henry7/PBR/subjects/"
working = "/working/henry_temp/PBR/"

mse_list = ["mse4530", "mse4981"]

for mse in os.listdir(base):
    if mse.startswith("mse"): 
          if os.path.exists(base + mse + "/lesion_mni_t2/"):
              if not os.path.exists(working + mse):
                  print("make:", working + mse)
                  os.mkdir(working + mse)
              try: 
                  shutil.copytree( base + mse + "/lesion_mni_t2/", working + mse + "/lesion_mni_t2/")
                  print("copying...", base + mse + "/lesion_mni_t2/", working + mse + "/lesion_mni_t2/")
                  shutil.rmtree(base + mse + "/lesion_mni_t2/")
              except:
                  pass

