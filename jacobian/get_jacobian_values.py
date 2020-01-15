import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import pandas as pd
from pbr.config import config
import shutil
import nibabel as nib
import nilearn
from nilearn import masking



def calc_median(masks):
    cmd = ["fslstats", masks, "-M"]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0]
    median = float(output[0])
    print(median)
    return median



def write_csv(msid, mse, mse_bl, bm, caud, o):
    df.loc[idx, "MSID"] = msid
    df.loc[idx, "MSE"] = mse
    df.loc[idx, "MSE_BL"] = mse_bl
    bm = str(bm)
    caud = str(caud)

    jacobianmask = glob("/data/henry10/PBR_long/subjects/*/jacobian/jacobian_masks/{}_*/".format(mse))

    if len(jacobianmask) > 0:
        jacobianmask = jacobianmask[0]
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", jacobianmask)
        for masks in os.listdir(jacobianmask):
            if len(bm) < 5:
                if "bm-jaco" in masks:
                    bm = jacobianmask + masks
                    df.loc[idx, "Jacobian Brain Mask"] = calc_median(bm)
                if "csf" in masks:
                    csf = jacobianmask + masks
                    df.loc[idx, "Jacobian CSF"] = calc_median(csf)
                if "gm-jaco" in masks:
                    gm = jacobianmask + masks
                    df.loc[idx, "Jacobian Gray Matter"] = calc_median(gm)
                if "wm-jaco" in masks:
                    wm = jacobianmask + masks
                    df.loc[idx, "Jacobian White Matter"] = calc_median(wm)
                if "pGM-jaco" in masks:
                    pGM = jacobianmask + masks
                    df.loc[idx, "Jacobian p Gray Matter"] = calc_median(pGM)
            if len(caud) < 5:
                if "BrainStem" in masks:
                    bs = jacobianmask + masks
                    df.loc[idx, "Jacobian Brain Stem"] = calc_median(bs)
                if "L-Accum" in masks:
                    l_acc = jacobianmask + masks
                    df.loc[idx, "Jacobian L Accumbens"] = calc_median(l_acc)
                if "L-Amy" in masks:
                    l_amy = jacobianmask + masks
                    df.loc[idx, "Jacobian L Amygdala"] = calc_median(l_amy)
                if "L-Caud" in masks:
                    l_caud = jacobianmask + masks
                    df.loc[idx, "Jacobian L Caudate"] = calc_median(l_caud)
                if "L-Hippo" in masks:
                    l_hip = jacobianmask + masks
                    df.loc[idx, "Jacobian L Hippocampus"] = calc_median(l_hip)
                if "L-Pall" in masks:
                    l_pall = jacobianmask + masks
                    df.loc[idx, "Jacobian L Pallidum"] = calc_median(l_pall)
                if "L-Put" in masks:
                    l_put = jacobianmask + masks
                    df.loc[idx, "Jacobian L Putamen"] = calc_median(l_put)
                if "L-Thal" in masks:
                    l_thal = jacobianmask + masks
                    df.loc[idx, "Jacobian L Thalamus"] = calc_median(l_thal)
                if "R-Accum" in masks:
                    r_acc = jacobianmask + masks
                    df.loc[idx, "Jacobian R Accumbens"] = calc_median(r_acc)
                if "R-Amy" in masks:
                    r_amy = jacobianmask + masks
                    df.loc[idx, "Jacobian R Amygdala"] = calc_median(r_amy)
                if "R-Caud" in masks:
                    r_caud = jacobianmask + masks
                    df.loc[idx, "Jacobian R Caudate"] = calc_median(r_caud)
                if "R-Hippo" in masks:
                    r_hip = jacobianmask + masks
                    df.loc[idx, "Jacobian R Hippocampus"] = calc_median(r_hip)
                if "R-Pall" in masks:
                    r_pall = jacobianmask + masks
                    df.loc[idx, "Jacobian R Pallidum"] = calc_median(r_pall)
                if "R-Put" in masks:
                    r_put = jacobianmask + masks
                    df.loc[idx, "Jacobian R Putamen"] = calc_median(r_put)
                if "R-Thal" in masks:
                    r_thal = jacobianmask + masks
                    df.loc[idx, "Jacobian R Thalamus"] = calc_median(r_thal)

    df.to_csv(o)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument('-o', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    o = args.o
    df = pd.read_csv("{}".format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        mse_bl = df.loc[idx, "mse1"]
        bm = caud = ""
        #bm = df.loc[idx, "Jacobian Brain Mask"]
        #caud = df.loc[idx, "Jacobian L Caudate"]
        write_csv(msid, mse, mse_bl,bm, caud, o)


