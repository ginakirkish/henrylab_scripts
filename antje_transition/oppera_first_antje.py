from glob import glob
from subprocess import check_call 
import os
import sys
from pbr.base import _get_output


run_first_t1 = '/data/henry6/gina/henrylab_utils/first_t1_input.py'

#import list with mseIDs
mse_list = sys.argv[1:][0]


# open the file passed as args.MSEID as f, strips off empty lines and /n in the txt file of mseids
with open(mse_list) as f:
    print(mse_list)
    mseid_list = list([x.strip() for x in f.readlines()])
    print(mseid_list)

    # iterate through each mseid in the file and run pbr first workflow
    for mseid in mseid_list:
        #mseid = 'mse{}'.format(mseid) #put "mse" if file does not contain mse<> in cell, because this is needed


        #check for each mseID if folder with bias field corrected images exists in PBR, if not, make a new folder
        #run N4 bias field correction algorithm from ants
        pbr_folder = glob('{0}/{1}/'.format(_get_output(mseid), mseid))
        N4corr = pbr_folder[0] + '/N4corr'
        nii = pbr_folder[0] + "/nii"
        if not (os.path.exists(N4corr)):
	        os.mkdir(N4corr)

        t1_file =  glob('{0}/{1}/nii/*BRAVO_IRSPGR_fa8_ti600.nii.gz'.format(_get_output(mseid), mseid))
        if t1_file:
            t1_N4corr = t1_file[0].replace('.nii','_N4corr.nii')
            cmd = ['N4BiasFieldCorrection', '-i', t1_file[0],'-o', t1_N4corr]
            check_call(cmd)
        else:
            print("missing {}" .format(mseid))

        cmd = ['python', run_first_t1, '-i', t1_N4corr ]
        #cmd = ['pbr', mseid, '-w', 'first', '-R'] #needs [0] as check_call does not take a list, therefore now it takes the first img and T1
        print(cmd)
        check_call(cmd)








    


