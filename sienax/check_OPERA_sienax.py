import pandas as pd
import pbr
from pbr.base import _get_output
import os
from subprocess import check_call, Popen
import json





df = pd.read_csv("/home/sf522915/Documents/OPERA_sienax.csv")


for _, row in df.iterrows():
    msid = str(row["msid"])
    mse = str(row['mseid'])
    print(msid, mse)
    sienax = _get_output(mse) + '/' + mse + '/sienax_t1manualseg/'
    if not os.path.exists(sienax):
        print("DOES NOT HAVE SIENAX LONG", _get_output(mse) + '/' + mse )

    else:

        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1]).replace(".nii", "_T1mni.nii")
                t1_file = _get_output(mse) + '/' + mse + '/alignment/baseline_mni/' + t1_file
                print(t1_file)
                #
                cmd = ["sienax_optibet", t1_file, "-lm", _get_output(mse) + '/' + mse + '/sienax_t1manualseg/lesion_mask.nii.gz',\
                       "-r", "-d", "-o", _get_output(mse) + '/' + mse + '/sienax_t1manseg/']
                if not os.path.exists(_get_output(mse) + '/' + mse + '/sienax_t1manseg/lesion_mask.nii.gz'):

                    print("sienax_optibet", t1_file, "-lm", _get_output(mse) + '/' + mse + '/sienax_t1manualseg/lesion_mask.nii.gz',\
                       "-r", "-d", "-o", _get_output(mse) + '/' + mse + '/sienax_t1manseg/')
                    Popen(cmd).wait()
        #cmd = ["fsleyes", sienax + "/I_brain.nii.gz", sienax + "/lesion.nii.gz" ]
        #Popen(cmd).wait()
        #print(cmd)