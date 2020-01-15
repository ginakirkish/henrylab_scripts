import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
from getpass import getpass
import json
import pandas as pd
from pbr.config import config

base_surf = "/data/henry6/PBR/surfaces/"

def run_FS_cross_sectional(msid, mse_list):
    recon = ""
    print("**************")
    print(msid, mse_list)
    for mse in mse_list:
        print(msid, mse)
        recon = glob("{}/{}-{}*".format(base_surf, msid, mse))
        if len(recon) > 0:
            recon = recon[0]
            print(recon)
            print(mse, "RECON HAS BEEN RUN")
        else:
            cmd = ["pbr", mse, "-w", "recon", "-R"]
            Popen(cmd).wait()
            recon = recon[0]

"""recon-all -base ms1049-average-template -tp ms1049-mse1827-002-AX_T1_3D_IRSPGR/ -tp ms1049-mse1828-003-AX_T1_3D_IRSPGR/ -all"""

def run_FS_base(msid, mse_bl, mse, free_long):
    recon_bl = glob("{}/{}-{}*".format(base_surf, msid, mse_bl))
    recon_tp2 = glob("{}/{}-{}*".format(base_surf, msid, mse))
    base_dir = free_long + mse + "_" + mse_bl
    if len(recon_bl) >0 and len(recon_tp2) >0:
        recon_bl = recon_bl[0]
        recon_tp2 = recon_tp2[0]
        cmd = ["recon-all", "-base", base_dir, "-tp", recon_bl, "-tp", recon_tp2, "-all" ]
        print(cmd)
        Popen(cmd).wait()

        cmd_bl = ["recon-all", "-long", recon_bl, base_dir, "-all"]
        print(cmd_bl)
        Popen(cmd_bl).wait()

        cmd_tp2 = ["recon-all", "-long", recon_tp2, base_dir, "-all"]
        print(cmd_tp2)
        Popen(cmd_tp2).wait()




def run_all(msid, mse_list):
    #cross sectionally process all time points with the default mode network
    run_FS_cross_sectional(msid, mse_list)

    free_long = config["long_output_directory"] +'/'+ msid + "/freesurfer_long/"
    if not os.path.exists(free_long): os.mkdir(free_long)

    mse_bl = mse_list[0]
    other_mse = mse_list[1:]
    for mse in other_mse:
        print(msid, mse_bl, mse)
        run_FS_base(msid, mse_bl, mse, free_long)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    df = pd.read_csv("{}".format(c))

    ms_bl_first = df['msid'].iloc[0]
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        mse_bl = df.loc[idx, "mse1"]
        if msid == ms_bl_first:
            mse_list.append(mse)
            #print(msid, mse_bl, mse, mse_list)
            #print("XXXXXXXXXXXXX")
        else:
            print(ms_bl_first, mse_list)

            run_all(ms_bl_first, mse_list)
            ms_bl_first = msid
            mse_list = []
            mse_list.append(mse)