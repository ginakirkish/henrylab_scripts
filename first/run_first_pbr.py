from subprocess import check_call
import os
from glob import glob
import argparse
from pbr.config import config 
import pandas as pd
from pbr.base import _get_output 
from subprocess import Popen, PIPE

df = pd.read_csv("/home/sf522915/Documents/epic_BLtoyr4_first.csv")

def run_pbr_align(mse):
    #from getpass import getpass
    alignment_folder = _get_output(mse) + "/{0}/alignment".format(mse)
    if os.path.exists(alignment_folder):
        cmd_rm = ['rm','-r', alignment_folder]
        #print (cmd_rm)
        proc = Popen(cmd_rm)
        proc.wait()
        #print("")

    #password = getpass("mspacman password: ")
    cmd = ['pbr', mse, '-w', 'align', '-R']
    #print (cmd)
    proc = Popen(cmd)
    proc.wait()


def run_first(mse): 
    cmd = ['pbr', mse, '-w', 'first', '-R']
    #print('python /data/henry6/gina/scripts/grid_submit.py "{0}"'.format("pbr " + mse + " -w nifti align first -R"))
    print (cmd)
    proc = Popen(cmd)
    proc.wait()

       
for idx, row in df.iterrows():
    mse = str(row["mse"])
    e = glob("/working/henry_temp/PBR/dicoms/{}/E*".format(mse))
    if len(e)>0:
        e = e[0]
        if not os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
        #print(mse, "ALIGNMENT BUT NO FIRST")
            run_first(mse)
    else:
        #print(mse)
        continue

    """if not os.path.exists(_get_output(mse) +"/"+ mse + "/alignment/status.json"):
       #print(_get_output(mse) +"/"+ mse)
       #print(mse, "NO ALIGNMENT FOLDER")
       run_pbr_align(mse)"""
    #if not os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
        #print(mse, "ALIGNMENT BUT NO FIRST")
        #run_first(mse)
   #else:
       #print(mse, "FIRST HAS BEEN RUN")


              
       
   

