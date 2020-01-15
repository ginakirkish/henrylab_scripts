from glob import glob
from subprocess import check_call
import os
import argparse
from pbr.base import _get_output

def run_sienax(mse_txt):
    # open the file passed as args.MSEID as f, strips off empty lines in the txt file of mseids
    with open(mse_txt, 'r') as f:
        mseid_list = [x.strip() for x in f.readlines()]
        print(mseid_list)

        # iterate through each mseid in the file
        for mseid in mseid_list:
            sienax_directory = ('{0}/{1}/sienax_optibet_t1manseg/'.format(_get_output(mseid), mseid))
            img = glob('{0}/{1}/nii/*_reorient.nii.gz'.format(_get_output(mseid), mseid))
            lm = glob('{0}/{1}/*/lesion_new.nii.gz'.format(_get_output(mseid), mseid))
            print(sienax_directory, img[0])

            if img and lm:
                cmd = ['sienax_optibet', img[0], '-lm', lm[0], '-r', '-d', '-o', sienax_directory]
                print(cmd)
                #check_call(cmd)
            else:
                print("missing {0}".format(mseid))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code run sienax on OPERA new lesion masks')
    parser.add_argument('MSEID', help ='txt file of the mseids you want to get')
    args = parser.parse_args()
    mse_txt = args.MSEID
    print(mse_txt)
    run_sienax(mse_txt)



    


