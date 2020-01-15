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


def get_date(mse):
    import subprocess
    date = ""
    proc = subprocess.Popen(["ms_get_phi", "--examID", mse, "-p",password],stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = str(line.rstrip())
        if "StudyDate" in   line:
            date=   line.split()[-1].lstrip("b'").rstrip("'")
            print("Date", date)
    return date

def get_mse(msid):
    msid_txt = glob("/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/*/" + msid + ".txt")
    if len(msid_txt)> 0:
        msid_txt = msid_txt[0]
        if os.path.exists(msid_txt):
            with open(msid_txt,'r') as f:
                timepoints = f.readlines()
                mse_bl = timepoints[0].replace("\n","")
                yr1 = timepoints[1].replace("\n","")
                try:
                    yr2 = timepoints[2].replace("\n","")
                except:
                    yr2 = ""
                info = {"Baseline": mse_bl, "F/U Yr 1": yr1, "F/U Yr 2":yr2}
                return info
        else:
            print ("no msid tracking txt file exists")
            return False


def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
        mse = get_mse(msid)
        print(mse)
        """mse1 = mse[0]
        mse2 = mse[1]
        mse3 = mse[2]
        date1 = get_date(mse1)
        date2 = get_date(mse2)
        date3 = get_date(mse3)
        print(mse1)
        #df.loc[idx, "VisitType"] =

    df.to_csv(out)"""







if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)