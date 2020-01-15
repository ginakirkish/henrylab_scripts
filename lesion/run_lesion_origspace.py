from subprocess import Popen, PIPE

from glob import glob
from subprocess import Popen
import pandas as pd
import pbr
from pbr.base import _get_output
import os
import json
import subprocess
import shutil

mse_txt = "/data/henry6/gina/scripts/mse_not_done.txt"

mselist = [line.rstrip('\n') for line in open(mse_txt)]



for mse in os.listdir("/data/henry7/PBR/subjects/"): #mse in mselist:
#for mse in mselist:
    #print(mse)

    if mse.startswith("mse") and not mse.endswith("B") and not mse.endswith(".gz"):

        mse_num = mse.replace("mse", "")
        try:


            if int(mse_num) > 1080 or int(mse_num) < 1080:

                #print(mse)
                try:
                    lesion_f = glob(_get_output(mse) + "/{0}/lesion_origspace_flair/lesion.nii.gz".format(mse))[0]
                except:
                    lesion_f = ""
                    pass
                try:
                    lesion_t2 = glob(_get_output(mse) + "/{0}/lesion_origspace_t2/lesion.nii.gz".format(mse))[0]
                except:
                    lesion_t2 = ""
                    pass
                if len(lesion_f) > 1:
                    lesion = lesion_f
                elif len(lesion_t2) > 1:
                    lesion = lesion_t2
                else:
                    #print(mse, "no lesion for this subject")
                    lesion = ""
                mse_pbr = _get_output(mse) + '/' + mse + '/alignment/status.json'
                #print(mse, lesion)
                if os.path.exists(mse_pbr):
                    with open(mse_pbr) as data_file:
                        data = json.load(data_file)
                        if len(data["t1_files"]) > 0:
                            t1 = data["t1_files"][-1]
                            if len(lesion) > 0:


                                sienax = lesion.split("/")[6].split("_")[-1]
                                sienax_orig = _get_output(mse) + '/' + mse + "/sienaxorig_" + sienax
                                final_les = _get_output(mse) + '/' + mse + "/lesion_origspace_" + sienax + '/'
                                lesion_final_new = final_les + "lesion.nii.gz"
                                #if int(mse_num) > 2594 :
                                if not os.path.exists(sienax_orig + "/I_stdmaskbrain_pve_2.nii.gz"):
                                    if not os.path.exists(sienax_orig + '/lesion_mask.nii.gz'):
                                        #sienax_optibet = "sienax_optibet {0} -lm {1} -r -d -o {2}".format(t1,lesion_final_new,sienax_orig)
                                        #print(sienax_optibet)
                                        #cmd = [sienax_optibet]
                                        #Popen(cmd).wait()

                                        #proc = Popen(cmd, stdout=PIPE)
                                        #output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                                        #print(sienax_optibet)
                                        #print(cmd)
                                        #print(output)
                                        #print("                   ")
                                        #print("python", "/data/henry6/gina/scripts/grid_submit.py",'"sienax_optibet', t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig +'"')
                                        cmd = ["sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig]
                                        print(cmd)
                                        Popen(cmd).wait()

                                        #print(sienax_optibet)
                                #print(cmd)
                                #proc = Popen('python /data/henry6/gina/scripts/grid_submit.py "{0}"'.format(cmd) , stdout=PIPE)
                                    #cmd = ["sienax_optibet", t1, "-lm", lesion_final_new, "-r", "-d", "-o", sienax_orig]
                                        #print(mse)
                                        #cmd = []
                                        #proc = Popen(sienax_optibet, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                        #proc.wait()
        except:
            pass


