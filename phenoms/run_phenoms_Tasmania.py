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
import subprocess

base_dir = '/data/henry12/phenoms/Tasmania/'

def rename(final_path):
    print(final_path, final_path.replace(" ","-"))
    os.rename(final_path, final_path.replace(" ","-"))

def get_brain(t1_path):
    BM = glob(t1_path + 'r*brain*.nii.gz')
    if len(BM) >= 1:
        for b in BM:
            if not "mask" in b:
                BM = b
    else:
        BM = ""
    return BM


def run_sienax(t1,out):
    t1_out = out
    #t1_out =  base_dir+ '/sienax_output/' + sub
    #if not os.path.exists(t1_out + '/I_brain.nii.gz'):
    if os.path.exists(t1):
        cmd = ["sienax_optibet", t1, "-r", "-d", "-o", t1_out ]
        print("sienax_optibet", t1, "-r", "-d", "-o", t1_out )
    try:
        Popen(cmd).wait()
    except:
        pass
        #print(t1_out, "SIENAX FILE EXISTS")


def run_first(t1,out):

    #sub = t1.split('_')[3:4]
    #odir =  base_dir + '/first_output/' + sub
    odir = out
    print("output", odir)
    if not os.path.exists(odir): os.mkdir(odir)
    if len(glob('{}/*firstseg*'.format(odir))) == 0:
    #x = 0
    #if x == 0:
        fname = t1.split('/')[-1].split('.nii')[0]
        oname = os.path.join(odir, fname)

        omat = oname+'_to_std_sub'

        flirt_job = ['first_flirt', t1, omat]
        mat_name = omat+'.mat'

        if not os.path.exists(mat_name):
            print(flirt_job)
            check_call(flirt_job)

        imsfirst = []
        imscorr = []
        for s in ['L_Accu', 'L_Amyg', 'L_Caud', 'L_Hipp', 'L_Puta', 'L_Thal', 'R_Accu', 'L_Pall',
                  'R_Amyg', 'R_Caud', 'R_Hipp', 'R_Pall', 'R_Puta', 'R_Thal', 'BrStem']:

            modelN = '336'
            bcorr = '1'
            intref = '0'
            if 'Accu' in s:
                nmodes = '50'
            elif 'Amyg' in s:
                nmodes = '50'
                intref = '1'
            elif 'Caud' in s:
                nmodes = '30'
                intref= '1'
            elif 'Hipp' in s:
                nmodes = '30'
                intref = '1'
            elif 'Late' in s:
                nmodes = '40'
                intref = '1'
            elif 'Pall' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'Puta' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'Thal' in s:
                nmodes = '40'
                bcorr = '0'
            elif 'Stem' in s:
                nomdes = '40'
            else:
                raise ValueError('The structure {} is not in the structure list'.format(s))

            imfirst = '{}-{}_first'.format(oname, s)
            imsfirst.append(imfirst)

            FSLDIR = '/netopt/fsl5'

            if intref == '0':
                if bcorr == '1':
                    cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                           '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/{}_bin.bmv'.format(FSLDIR, modelN, s)]
                else:
                     cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                           '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/05mm/{}_05mm.bmv'.format(FSLDIR, modelN, s)]
            else:
                cmd = ['{}/bin/run_first'.format(FSLDIR), '-i', t1, '-t', mat_name,
                       '-n', nmodes, '-o', imfirst, '-m', '{}/data/first/models_{}_bin/intref_thal/{}.bmv'.format(FSLDIR, modelN, s), '-intref', '{}/data/first/models_{}_bin/05mm/{}_Thal_05mm.bmv'.format(FSLDIR, modelN, s.split('_')[0])]
            print('\nRunning Segmentation {} with: {}'.format(s,cmd))
            check_call(cmd)

            imcorr = '{}-{}_corr'.format(oname, s)
            imscorr.append(imcorr)

            btype = 'fast'
            if bcorr != '1': btype='none'
            cmd = ['{}/bin/first_boundary_corr'.format(FSLDIR), '-s', imfirst, '-o', imcorr,
                   '-i', t1, '-b', btype]
            print(cmd)
            check_call(cmd)

        cmd = ['{}/bin/fslmerge'.format(FSLDIR), '-t', '{}_all_{}_firstsegs'.format(oname, btype)]


        for imCORR in imscorr:
            if os.path.exists(imCORR + '.nii.gz'):
                cmd.append(imCORR+'.nii.gz')
                print(cmd)

        print(cmd)
        check_call(cmd)

        cmd = ['{}/bin/fslmerge'.format(FSLDIR), '-t', '{}_all_{}_origsegs'.format(oname, btype)]
        for imname in imsfirst:
            if os.path.exists(imname + '.nii.gz'):
                cmd.append(imname+'.nii.gz')
        print(cmd)
        check_call(cmd)

        cmd =  ['{}/bin/first_mult_bcorr'.format(FSLDIR),'-i', t1, '-u', '{}_all_{}_origsegs'.format(oname, btype),
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', '{}_all_{}_firstsegs'.format(oname, btype)]
        print('{}/bin/first_mult_bcorr'.format(FSLDIR),'-i', t1, '-u', '{}_all_{}_origsegs'.format(oname, btype),
                '-c', '{}_all_{}_firstsegs'.format(oname, btype), '-o', '{}_all_{}_firstsegs'.format(oname, btype))
        check_call(cmd)


def bias_corr(t1):
    N4 = t1.replace(".nii","_N4.nii")
    if not "N4" in t1:
        if not os.path.exists(N4):
            #print("N4BiasFieldCorrection", "-d", "3", "-i", t1,"-o",N4 )
            cmd = ["N4BiasFieldCorrection", "-d", "3", "-i",t1,"-o",N4]
            Popen(cmd).wait()
    return N4

def run_reorient(t1):
    cmd = ["fslreorient2std", t1, t1.replace(".nii","reorient.nii")]
    #print("fslreorient2std", t1, t1.replace(".nii","reorient.nii"))
    Popen(cmd).wait()
    t1 = t1.replace(".nii","reorient.nii")
    return t1

def run_all(t1,sub):
    
    if not "reorient" in t1:
        reorient = run_reorient(t1)
    else:
        reorient = t1
    if not "N4" in reorient:
        N4 = bias_corr(reorient)
    else:
        N4 = reorient
    #print(reorient)
    #print(N4)
    #run_sienax(N4, sub)
    
    run_first(N4, sub)


def convert_dcm2nii(E):
    cmd = ["dcm2nii", E]
    Popen(cmd).wait()


def run_dcm(t1):
    print(t1)
    #cmd = ["fslview", t1 + "/20*.nii.gz"]
    #Popen(cmd).wait()
    cmd = ["dcm2nii", t1 ]
    print(cmd)
    Popen(cmd).wait()

def check_dim(t1):
    cmd = ["fslhd", t1]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    dim1, dim2, dim3 = "","",""
    for l in output:
        if "pixdim1" in l:
            dim1 = l[-1]
        if "pixdim2" in l:
            dim2 = l[-1]
        if "pixdim3" in l:
            dim3 = l[-1]
    return dim3
    #print(dim1, dim2, dim3)



df = pd.read_csv("/data/henry12/phenoms/csv/tasmania_current.csv")
for idx in range(len(df)):
    sub_id = df.loc[idx, 'subjects']
    date = df.loc[idx, "date"]
    t1 = df.loc[idx, "T1"]
    first_output = "{}/first_output/{}_{}_{}/".format(base_dir,sub_id, date, t1)
    sienax_output = "{}/sienax_output/{}_{}_{}/".format(base_dir,sub_id, date, t1)
    t1 = glob("{}/{}/iSiteExport/{}*{}/2*.nii.gz".format(base_dir,sub_id, date, t1))
    #run_sienax(t1, sienax_output)

    if len(t1) > 0:
        t1 = t1[0]
        #if not os.path.exists(first_output):
        """try:
            run_first(t1, first_output)
        except:
            pass"""
        #else:
            #print(first_output)
        #if not os.path.exists(sienax_output + "/I_brain.nii.gz"):
        run_sienax(t1, sienax_output)
        #else:
            #print(sienax_output)
            
    


"""t1_file = ["AxFSPGR3D","AxT1PREVOL","AxT1+CVOL","3mmT1sag","3mmSagT1BRAIN","3mmCorT1BRAIN","3mmAxT1BRAIN","T1SAG3MM","T1Cor3mm","T1Ax3mm",
"3mmT1cor","3mmT1ax","T1VolumeAquiredSagittal","T1AxSPGR3D","T1axVolSPGR","T1axVOLSPGR","T1axSPGRVOL","AxSPGRAST1.2m","AxSPGR1.2mVol","Ax1.2mVolSPGR",
"T1TraTIRM+C",
"T13mmCorBrain",
"t1_tse_sag101",
"AxT1FLAIR",
"T1axFLAIR",
"T13mmCorBrain", "SPGR"]

subjects = glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/20*/2**.nii.gz")
for t1 in subjects:
    dim = check_dim(t1)
    #print("#####", dim, t1, )
    try:
        if float(dim) < 3.0:
            for t1_name in t1_file:
                if t1_name in t1:
                    print("*****************")
                    #print(dim, t1)
                    sub = t1.split('/')[5] +"_"+ t1.split('/')[7]
                    #print(sub)
                    run_all(t1,sub)
    except:
        pass"""
    
    
    
    
"""date = t1.split('/')[-1].split("_")[0]
                nifti_path = "/data/henry12/phenoms/Tasmania/{}/iSiteExport/nii/".format(t1.split('/')[5])
                date_path = nifti_path +date[0:8]
                series_path = date_path +'/'+ t1.split('/')[8]
                if not os.path.exists(nifti_path):
                    os.mkdir(nifti_path)
                if not os.path.exists(date_path):
                    os.mkdir(date_path)
                if not os.path.exists(series_path):
                    os.mkdir(series_path)
                shutil.copyfile(t1, series_path +'/'+ t1.split('/')[-1])
                #print(nifti_path)
                #print(date_path)
                #print(series_path)
                #print(t1, series_path +'/'+ t1.split('/')[-1])
                t1 = series_path +'/'+ t1.split('/')[-1]
                print(t1)
                sub = t1.split('/')[5] + '_' + t1.split('/')[8] +'_' + t1.split('/')[9]
                print(t1, sub)
                run_all(t1, sub)"""



"""

subjects = glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/DICOM")
for x in subjects:
    print("********************")#, x.split('/')[5])
    t1 = os.listdir(x)

    #print(t1)
    for t1 in os.listdir(x):
        #print(x + t1)
        for z in os.listdir(x +'/'+ t1):
            t_file = glob('{}/{}/*.nii.gz'.format(x, t1))
            for items in t_file:
                #print( items)
                dim = check_dim(items)
                if float(dim) < 3.0:
                    print(dim, t1)
    T1 = ""




    for t1_name in t1_file:
        if t1_name in t1:
            t1_path = glob(str('{}/{}/20*'.format(x, t1_name)))
            #print(t1_path)"""
"""for T in t1_path:
                dim = check_dim(T)
                if float(dim) < 3.0:
                    print(dim, T.split('/')[8])"""

            #print(t1 + t1_name, "*****")

            #T1 = t1_name
    #print(T1)
    #t1_name = x + '/' + T1
    #print(t1_name + "/*.nii.gz")
    #print(t1_name.split("/")[8])
    #run_dcm(t1_name)
    #sub = t1_name.split('/')[5].split('_')[4]
    #print(sub)




"""subjects = glob('{}/*/iSiteExport/DICOM/dicom/*.dcm'.format(base_dir))
for t1 in subjects:
    #print(t1)
    cmd = ["dcmdump", t1]
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = str(line.rstrip())
        if "SeriesDescription" in line:
            #print(line, "&&&&&&&&&&&&&&&")
            series =  str(line.split()[2:6]) #.lstrip("b'").rstrip("'")
            series = series.replace("[","").replace("'","").replace("#","").replace("]","").replace(" ","").replace(",","").replace("(","").replace(")","").replace("/","")
            #t1_new = base_dir + t1.split("/")[6] +'/'+ t1.split("/")[7] + "/DICOM/" + series + '/'

            t1_new = base_dir + t1.split("/")[5] +'/iSiteExport/'+ "/DICOM/" + series + '/'
            print(t1_new)
            if not os.path.exists(t1_new):
                os.mkdir(t1_new)
                print(t1_new)
            print(t1,t1_new + '/' + t1.split('/')[-1])
            shutil.copyfile(t1,t1_new + '/' + t1.split('/')[-1])"""




#for files in os.listdir(s):
"""if t1.endswith(".nii"):
        #print(files)

        sub = t1.split('/')[5].split('_')[4]
        print(t1, sub)
        run_all(t1, sub)"""
