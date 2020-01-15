import numpy as np
import os
import pandas as pd
import argparse
from os.path import join
import csv
from subprocess import Popen, PIPE
from glob import glob
import matplotlib.pyplot as plt
from subprocess import check_output
import shutil
from getpass import getpass

df = pd.read_csv("/home/sf522915/esha_mse.csv")
#password = getpass("mspacman password: ")
for _, row in df.iterrows():
    mse = row["MSEID"]
    mse = mse.replace("mse", "")
    cmd = ["ms_get_patient_id", "--exam_id", str(mse)]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    
    print(lines)
    print(mse)
