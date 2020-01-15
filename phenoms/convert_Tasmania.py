import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json, uuid
from nipype.utils.filemanip import load_json
from subprocess import Popen, PIPE
import pandas as pd
import shutil
import subprocess

base_dir = '/data/henry12/phenoms/Tasmania/'
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


subjects = glob('{}/*/iSiteExport/DICOM/*.dcm'.format(base_dir))
"""for t1 in subjects:
    print("***************")
    series, date = "", ""
    cmd = ["dcmdump", t1]
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = str(line.rstrip())
        if "SeriesDescription" in line:
            series =  str(line.split()[2:6])
            series = series.replace("[","").replace("'","").replace("#","").replace("]","").replace(" ","").replace(",","").replace("(","").replace(")","").replace("/","")
        if "StudyDate" in line:
            date = str(line.split()[2:6])
            date = date.replace("[","").replace("'","").replace("#","").replace("]","").replace(" ","").replace(",","").replace("(","").replace(")","").replace("/","")
        print(series, date)
        if len(series) > 3 and len(date) > 4: 

            t1_new = base_dir + t1.split("/")[5] +'/iSiteExport/' + date + "_" + series + '/'
            print(t1_new)
            if not os.path.exists(t1_new):
                os.mkdir(t1_new)
                print("################",t1_new)
            print(t1,t1_new + '/' + t1.split('/')[-1])
            print("%%%%%%%%%%%%%%%%%%%%%")
            try:
                shutil.move(t1,t1_new + '/' + t1.split('/')[-1])
            except:
                pass
            if "SPGR" in t1_new:
 
 
                cmd = ["dcm2nii",t1_new + '/']
                print("dcm2nii",t1_new + '/')
                print("$$$$$$$$$$$$$$$$$$$$$$$$")
                Popen(cmd).wait()"""
files = glob('{}/*/iSiteExport/2*'.format(base_dir))
t1_file = ["AxT1PREVOL","AxT1+CVOL","3mmT1sag","3mmSagT1BRAIN","3mmCorT1BRAIN","3mmAxT1BRAIN","T1SAG3MM","T1Cor3mm","T1Ax3mm",
"3mmT1cor","3mmT1ax","T1VolumeAquiredSagittal","T1AxSPGR3D","T1axVolSPGR","T1axVOLSPGR","T1axSPGRVOL","AxSPGRAST1.2m","AxSPGR1.2mVol","Ax1.2mVolSPGR",
"T1TraTIRM+C",
"3mmCorT1BRAIN",
"3mmSagT1BRAIN",
"3mmT1cor",
"3mmT1sag",
"T13mmCorBrain",
"T13mmCorBrain",
"T13mmSagBrain",
"T13mmSagBrain",
"T1Cor3mm",
"T1TraTIRM+C"
"T13mmCorBrain",
"T13mmSagBrain",
"T1Cor3mm",
"T1Ax3mm",
"t1_tse_sag101",
"T1SagSE",
"T1AxSE",
"T1SagSE",
"T1Ax3mm",
"AxT1FLAIR",
"T1axFLAIR",
"T13mmSagBrain",
"T13mmCorBrain",
"AxT1FSE",
"AXT1SETR"]

for series in files:
    print(series)
    cmd = ["dcm2nii",series]
    print("dcm2nii",series)
    print("$$$$$$$$$$$$$$$$$$$$$$$$")
    Popen(cmd).wait()
    """for t1 in t1_file:
        if t1 in series:
            print(t1)"""



"""subjects = glob("/data/henry12/phenoms/Tasmania/*/iSiteExport/DICOM")
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
"""
