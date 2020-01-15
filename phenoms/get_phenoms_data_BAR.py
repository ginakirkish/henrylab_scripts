
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json, uuid
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from subprocess import Popen, PIPE, check_call, check_output
import pandas as pd
import shutil

base_dir = '/data/henry12/phenoms/IDIBAPS/disk5s1/MulipleMS_Retrospective'

def get_les(t1_path):
    lesion = glob(t1_path + 'r*les*.nii.gz')
    if len(lesion) >= 1:
        lesion = lesion[0]
    else:
        lesion = ""
    return lesion

def get_t1(t1_path):
    t1_file = glob(t1_path + 'r*MPRAGE*.nii.gz')
    T1 = ""
    if len(t1_file) >= 1: #and not "les" in t1_file and not "brain_mask" in t1_file:
        for t1 in t1_file:
            if not "les" in t1 and not "brain" in t1:
                T1 = t1
    else:
        T1 = ""
    return T1

def get_brain_mask(t1_path):
    BM = glob(t1_path + 'r*brain_mask*.nii.gz')
    if len(BM) >= 1:
        BM = BM[0]
    else:
        BM = ""
    return BM

def get_brain(t1_path):
    BM = glob(t1_path + 'r*brain*.nii.gz')
    if len(BM) >= 1:
        if not "mask " in BM:
            BM = BM[0]
    else:
        BM = ""
    return BM


def write_csv(c,out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):

        ID = df.loc[idx, 'ID']
        year = df.loc[idx, 'year']
        year = year.replace("Ano","")
        path = glob('/{}/{}/*{}/'.format(base_dir, ID, year))
        path2 = glob('/{}/Imag*/{}/*{}/'.format(base_dir, ID, year))
        print("EXISTS", path2)
        if len(path) >=1:
            t1_path = path[0] + '/T1MPRAGE/'
            if os.path.exists(t1_path):
                t1 = get_t1(t1_path)
                brain_mask = get_brain_mask(t1_path)
                lesion = get_les(t1_path)
                df.loc[idx, 'T1'] = t1
                df.loc[idx, 'Lesion'] = lesion
                df.loc[idx, 'Brain Mask'] = brain_mask
        elif len(path2) >= 1:
            print(path2)
            t1_path = path2[0] + '/T1MPRAGE/'
            if os.path.exists(t1_path):
                t1 = get_t1(t1_path)
                brain_mask = get_brain_mask(t1_path)
                lesion = get_les(t1_path)
                df.loc[idx, 'T1'] = t1
                df.loc[idx, 'Lesion'] = lesion
                df.loc[idx, 'Brain Mask'] = brain_mask
    df.to_csv('{}'.format(out))





""""import csv
writer = open("/home/sf522915/Documents/phenoms.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["N-ID", "Year", "T1", "brain_mask","lesion_mask"])
for N in os.listdir(base_dir):
    row = {}
    if N.startswith('N'):
            new_path = base_dir + N
            for files in os.listdir(new_path):
                final_path = new_path +'/'+ files
                #rename(final_path)
                N = final_path.split('/')[6] + "_" + final_path.split('/')[7]
                if os.path.exists(final_path + '/T1MPRAGE/'):

                    t1_path = final_path + '/T1MPRAGE/'
                    t1_find = glob(final_path + '/T1MPRAGE/*')
                    if len(t1_find) >= 1:
                        print(t1_path)
                        les = get_les(t1_path)
                        t1 = get_t1(t1_path)
                        bm = get_brain_mask(t1_path)
                        brain = get_brain(t1_path)
                        row = {"N-ID" : final_path.split('/')[6],
                            "Year":final_path.split('/')[7],
                            "T1": t1, "brain_mask": bm, "lesion_mask": les}


                        spreadsheet.writerow(row)
writer.close()"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)

