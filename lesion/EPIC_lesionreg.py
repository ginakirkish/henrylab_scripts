from subprocess import Popen, PIPE

from glob import glob
from subprocess import Popen
import pandas as pd
import pbr
from pbr.base import _get_output
import os
import json
import subprocess

#mseid = [ "mse5275", "mse8850","mse4798", "mse6666","mse6463", "mse5382", "mse285", "mse4058", "mse1631", "mse1632", "mse7590","mse6843","mse4330","mse56", "mse5630"]
#mseid = ["mse5276", "mse7209", "mse5630", "mse4829", "mse7871", "mse6684", "mse6401", "mse8937", "mse4514", "mse4516","mse5780", "mse4548", "mse5858", "mse386"]
#df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_datanewNEWFINALGINA.csv")

#for idx in range(len(df)):
for mse in mseid:
    #mse = df.loc[idx, 'mse']

    if mse.startswith("mse") and not mse.endswith("B") and not mse.endswith(".gz"):
        mse_num = mse.replace("mse", "")
        #print(mse)
        lesion = ""
        affine = ""
        try:
            lesion = glob(_get_output(mse) + "/{0}/sienax_t2/lesion_mask.nii.gz".format(mse))[0]
        except:
            pass
        try:
            lesion = glob(_get_output(mse) + "/{0}/sienax_flair/lesion_mask.nii.gz".format(mse))[0]
        except:
            pass
        try:
            affine = glob(_get_output(mse)+ "/{0}/alignment/*_affine.mat".format(mse))[0]
        except:


            pass
        #print(lesion, affine)
        if len(lesion) > 0:
            sienax = lesion.split("/")[6].split("_")[1]
            if len(affine) > 0:

                inverse_aff = affine.replace(".mat", "_inv.mat")
                mse_pbr = _get_output(mse) + '/' + mse + '/alignment/status.json'
                if len(affine) > 0:

                    if os.path.exists(mse_pbr):
                        with open(mse_pbr) as data_file:
                            data = json.load(data_file)
                            if len(data["t1_files"]) > 0:
                                t1 = data["t1_files"][-1]
                            final_les = _get_output(mse) + '/' + mse + "/lesion_origspace_" + sienax + '/'
                            if not os.path.exists(final_les):
                                os.mkdir(final_les)
                            if os.path.exists(affine):
                                #if not os.path.exists(final_les + "lesion.nii.gz"):
                                cmd = ["/netopt/fsl5/bin/convert_xfm", "-omat", inverse_aff, "-inverse", affine]
                                print(cmd)
                                Popen(cmd, stdout=PIPE).wait()

                                cmd2 = ["flirt", "-applyxfm", "-init", inverse_aff, "-in",lesion,"-ref",t1, "-out",final_les + "lesion.nii.gz"]
                                print(cmd2)
                                proc = Popen(cmd2, stdout=PIPE)
                                proc.wait()

                                lesion_final_new = final_les + "lesion.nii.gz"
                                sienax_orig = _get_output(mse) + '/' + mse + "/sienaxorig_" + sienax
                                #if os.path.exists(_get_output(mse)+'/'+mse+"/sienaxorig_" + sienax + '/lesion_mask.nii.gz'):
                                    #print("")
                                    #print("python", "/data/henry6/gina/scripts/grid_submit.py",'"sienax_optibet', t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig +'"')
                                    #cmd = ["python", "/data/henry6/gina/scripts/grid_submit.py",'"sienax_optibet', t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig +'"']
                                cmd = ["sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig]
                                print("sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig)
                                proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                proc.wait()

