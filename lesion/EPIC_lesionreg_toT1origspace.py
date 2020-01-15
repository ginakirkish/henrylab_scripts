from subprocess import Popen, PIPE

from glob import glob
from subprocess import Popen
import pandas as pd
import pbr
from pbr.base import _get_output
import os
import json
import subprocess


pbr_folder = ["/data/henry7/PBR/subjects/", "/data/henry11/PBR/subjects/"]

for h in pbr_folder:
    for mse in os.listdir(h):
        print(mse)

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
                                    sienax_orig = _get_output(mse) + '/' + mse + "/sienaxorig_" + sienax
                                    if not os.path.exists(sienax_orig):
                                        cmd = ["/netopt/fsl5/bin/convert_xfm", "-omat", inverse_aff, "-inverse", affine]
                                        print(cmd)
                                        Popen(cmd, stdout=PIPE).wait()

                                        cmd2 = ["flirt", "-applyxfm", "-init", inverse_aff, "-in",lesion,"-ref",t1, "-out",final_les + "lesion.nii.gz"]
                                        print(cmd2)
                                        proc = Popen(cmd2, stdout=PIPE)
                                        proc.wait()

                                        lesion_final_new = final_les + "lesion.nii.gz"

                                        #subprocess.check_call(["python", "/data/henry6/gina/scripts/grid_submit.py","{0}".format("sienax_optibet "+ t1 + " -lm " + lesion_final_new +" -r "+"-d " +"-o "+ sienax_orig)])

                                        print("python", "/data/henry6/gina/scripts/grid_submit.py","{0}".format("sienax_optibet "+ t1 + " -lm " + lesion_final_new +" -r "+"-d " +"-o "+ sienax_orig))
                                        cmd = ["sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig]
                                        print("sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig)
                                        proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                        proc.wait()
