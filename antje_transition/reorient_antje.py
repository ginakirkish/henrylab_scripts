import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from subprocess import Popen


def get_align(mse):
    t1_file = ""
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1]
    return t1_file


text_file = "/data/henry6/gina/mse/mse_antje.txt"
with open(text_file) as f:
    lines = f.readlines()
    for x in lines:
        mse = x.rstrip('\n')
        mse = "mse" + mse.replace("mse", "").lstrip("0")
        print(mse)
        print(_get_output(mse))
        t1 = get_align(mse)
        reorient = t1.replace(".nii", "_reorient.nii")
        if "MPRAGE" in t1 and not "reorient" in t1:
            print(t1, reorient)
        Popen(["fslreorient2std", t1, reorient]).wait()
