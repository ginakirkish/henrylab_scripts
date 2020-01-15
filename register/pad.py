from subprocess import check_call, PIPE, Popen
from time import time
import argparse
import json
import pbr
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd
import nilearn

def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file


def run_nrigid( mse1, mse2):
    tp1_brain = get_t1(mse1)
    tp2_brain = get_t1(mse2)
    print(tp1_brain, tp2_brain)
    mni_pad = "/data/henry6/gina/nochop/mnipaddy.nii.gz"
    chop = "/data/henry6/gina/nochop/chop2.mat"

    cmd = ["flirt", "-in", tp1_brain, "-ref", mni_pad, "-out", tp1_brain.replace(".nii", "_pad.nii") , "-init", chop, "-applyxfm" ]
    check_call(cmd)
    print(cmd)

    cmd = ["flirt"]
    #nilearn.image.resample(tp1_brain, target_affine=None, target_shape=None, interpolation='continuous', copy=True, order='F', clip=True, fill_value=0)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-mse1', help = 'MSE1 - Moving subject')
    parser.add_argument('-mse2', help = 'MSE2 - Reference Subject')
    args = parser.parse_args()
    mse1 = args.mse1
    mse2 = args.mse2
    mse1_t1 = get_t1(mse1)
    mse2_t1 = get_t1(mse2)
    run_nrigid(mse1, mse2)