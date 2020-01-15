import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import subprocess
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
import nibabel as nib
from nipype.algorithms.metrics import ErrorMap, Distance, Overlap, Similarity
import pandas as pd
from nipype.interfaces.fsl import CopyGeom
import time





if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        c = check_mni(mse)
        df.loc[idx, "lesion error"] = c[0]
        df.loc[idx, "sienax"] = c[1]

    df.to_csv("{}".format(out))