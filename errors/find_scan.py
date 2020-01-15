import pandas as pd
import argparse
import csv
import pandas as pd
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json


def find_hardi(c):
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        #extracting the msid and mse from the csv file that you give as an arument
        msid = row["msid"]
        mse = row['mse']

        #looks within the status.json file to find the files that you are looking for
        if os.path.exists(_get_output(mse) + '/' + mse + '/nii/status.json'):

            with open(get_nifti(mse)) as data_file:
                data = json.load(data_file)

                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1].split('/')[-1]
                    print(t1_file)

                if len(data["nifti_files"]) > 0 :
                    niftis = data["nifti_files"]

                    if "hardi" in niftis:
                        print(niftis)



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for a hardi scan given a csv, i.e, python find_hardi.py -c ***.csv')
    parser.add_argument('-c', help = 'csv containing the msid')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    find_hardi(c)