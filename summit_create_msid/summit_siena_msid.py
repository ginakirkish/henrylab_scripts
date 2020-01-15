import numpy as np
import os
import pandas as pd
import argparse
import subprocess
from subprocess import Popen, PIPE
from glob import glob
import csv
from subprocess import check_output
import shutil
import pbr
from pbr.base import _get_output
import json
import math





df = pd.read_csv("/home/sf522915/Documents/summit.csv")






for _, row in df.iterrows():
    msid = "ms" + str(row["MSID"])
    bl = "mse" + str(row['Baseline'])
    yr1 = "mse" + str(row['12M'])
    yr2 = "mse" + str(row['24M'])
    yr10 = "mse" + str(row['120M'])
    print(bl, yr1, yr2, yr10)
    base_dir = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/all/"
    file = open(base_dir + msid + ".txt", "w")

    file.write(bl + "\n")
    file.write(yr1 + "\n")
    file.write(yr2  + "\n")
    file.write(yr10)
    file.close()
