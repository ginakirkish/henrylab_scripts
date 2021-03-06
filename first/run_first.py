from subprocess import check_call
import os
from glob import glob
import argparse
from pbr.config import config 
import pandas as pd
from pbr.base import _get_output 
from subprocess import Popen, PIPE



#df = pd.read_csv("/home/sf522915/check_process_roland.csv")
df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_dataCOMBINED_scannerinfo_Nov302018.csv")

def run_pbr_align(mse):
    from getpass import getpass
    alignment_folder = _get_output(mse) + "/{0}/alignment".format(mse)
    if os.path.exists(alignment_folder):
        cmd_rm = ['rm','-r', alignment_folder]
        print (cmd_rm)
        proc = Popen(cmd_rm)
        proc.wait()
        print("")

    password = getpass("mspacman password: ")
    cmd = ['pbr', mse, '-w', 'align', '-R', "-ps", password]
    print (cmd)
    proc = Popen(cmd)
    proc.wait()


def run_first(mse): 
    cmd = ['pbr', mse, '-w', 'first', '-R']
    print (cmd)
    proc = Popen(cmd)
    proc.wait()

       



for idx, row in df.iterrows():
    mse =str(row["mse"])
    msid = str(row["msid"])
    #print(mse)
    """if not os.path.exists(_get_output(mse) +"/"+ mse + "/alignment/status.json"):
       #print(_get_output(mse) +"/"+ mse)
       print(msid, mse, "NO ALIGNMENT FOLDER")
       #run_pbr_align(mse)
   elif os.path.exists(_get_output(mse) +"/"+ mse + "/sienax_flair/"): 
       print(msid, mse, "EVERYTHING IS COMPLETE")
   else:
       print(msid, mse, "SIENAX_FLAIR DOES NOT EXIST")"""

    if not os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
        print(mse, "ALIGNMENT BUT NO FIRST")
        run_first(mse)
    #else:
        #print(mse, "FIRST HAS BEEN RUN")


              
       
   
