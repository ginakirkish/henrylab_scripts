

import os
from glob import glob
from subprocess import Popen, PIPE
import json
import argparse
import pandas as pd
import pbr
from pbr.base import _get_output



def get_t1(mseid):
     if os.path.exists(_get_output(mseid)+"/"+mseid+"/alignment/status.json"):
        with open(_get_output(mseid)+"/"+mseid+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:

                t1_file = "none"
                print("no T1 file")
            else:
                t1 = data["t1_files"][-1].replace(".nii.gz", "")
                t1_file= data["t1_files"][-1]
                t1_file = t1_file.split("alignment")[0] + "/alignment/baseline_mni/" + t1_file.split('/')[-1].replace('.nii', "_T1mni.nii")
        return t1_file



def run_sienax(c):
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        mseid = str(row["mse"])
        timepoint = str(row["timepoint"])

        print(mseid)
        #if timepoint == "Baseline":
        if os.path.exists(_get_output(mseid)+"/"+mseid+"/alignment/status.json"):
            with open(_get_output(mseid)+"/"+mseid+"/alignment/status.json") as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) == 0:

                    t1_file = "none"
                    print("no T1 file")
                else:
                    t1 = data["t1_files"][-1].split('/')[-1].replace(".nii.gz", "")



        cmd = ["fslview", get_t1(mseid) , _get_output(mseid)+ '/' + mseid + "/lesion_mni_t2/lesion_final_new.nii.gz"]
        print("fslview", get_t1(mseid) , _get_output(mseid)+ '/' + mseid + "/lesion_mni_t2/lesion_final_new.nii.gz")
        proc = Popen(cmd)
        proc.wait()

        """cmd = ["sienax_optibet",get_t1(mseid) ,"-r", "-d", "-o", _get_output(mseid) + "/" + mseid + "/sienax/" + t1]
        print(cmd)
        #print("sienax_optibet",get_t1(mseid) , "-lm", _get_output(mseid)+ '/' + mseid + "/lesion_t1_mni/lesion_final_new.nii.gz", "-r", "-d", "-o", _get_output(mseid) + "/" + mseid + "/sienax_t2/")
        proc = Popen(cmd)
        proc.wait()"""

        """cmd = ["sienax_optibet",get_t1(mseid) , "-lm", _get_output(mseid)+ '/' + mseid + "/lesion_t1_mni/lesion_final_new.nii.gz", "-r", "-d", "-o", _get_output(mseid) + "/" + mseid + "/sienax_t2/"]
        print("sienax_optibet",get_t1(mseid) , "-lm", _get_output(mseid)+ '/' + mseid + "/lesion_t1_mni/lesion_final_new.nii.gz", "-r", "-d", "-o", _get_output(mseid) + "/" + mseid + "/sienax_t2/")
        proc = Popen(cmd)
        proc.wait()"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser('')
    parser.add_argument('-i', help = 'mse')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    print(c)
    print("*********************************")
    run_sienax(c)
