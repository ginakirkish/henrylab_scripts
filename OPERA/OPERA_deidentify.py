import os
from glob import glob
from subprocess import Popen, PIPE

import argparse
import shutil
import pandas as pd
import csv
import pbr
from pbr.base import _get_output


df = pd.read_csv("/home/sf522915/Documents/all_OPERA.csv")

OPERA_dir = "/data/henry6/OPERA/"

for _, row in df.iterrows():
    msid = row['msid']
    mse = row["mse"]
    subID = row["subject_id"]
    opera_id = row["OPERA_ID"]
    yr = row["yr"]
    tp = row["timepoint"]
    #print(msid, mse, subID, opera_id, yr)

path = "//data/henry6/OPERA/subj010/Subj010_102513/"

for files in os.listdir(path):

    if files.startswith("E"):
        cmd = ["svk_gepfile_anon.dev", "-i", path + files, "--deid_id", "1927090"]
        proc = Popen(cmd)
        proc.wait()
        print(cmd)

    """


    for files in os.listdir(OPERA_dir + subID):
        for path, dirs, files in os.walk(OPERA_dir + subID + files):
            for d in dirs:
                for f in glob.iglob(os.path.join(path, d, '*')):
                    print(f)





        cmd = ["rdump_dev", "-p",OPERA_dir + subID]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        print(output)

        for files2 in os.listdir(OPERA_dir + subID +'/'+ files):
            cmd = ["rdump_dev", "-p",OPERA_dir + subID + files]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            print(output)"""





            #if tp in files:
            #print(tp, OPERA_dir, subID)
            #for e in os.listdir(OPERA_dir + subID + '/' + files