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

def check_json(mse):
    nii = _get_output(mse)+"/"+mse+"/nii/status.json"
    if os.path.exists(nii):
        with open (nii) as data_file:
            data  = json.load(data_file)

            file = ["t1_files", "t2_files", "affine", "flair_files"]
            #for sq in file:
                #print(sq)
            if len(data["t1_files"]) > 0:
                seq = data["t1_files"]
                for data in seq:
                    if "reorient" in data:

                        #print(data)
                        #print(nii)
                        print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{0} {1} {2} {3} {4} {5}"'.format("pbr", mse,"-w", "nifti", "align", "-R"))
                        #cmd = ["pbr", mse, "-w", "nifti", "align", "-R"]
                        #Popen(cmd).wait()

def run_nifti_align(mse):
    #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{0} {1} {2} {3} {4} {5}"'.format("pbr", mse,"-w", "nifti", "align", "-R"))
    cmd = ["pbr", mse, "-w","nifti","align","-R"]
    Popen(cmd).wait()

def edit_json(mse):
    if mse == "mse6780":
        nii = _get_output(mse)+"/"+mse+"/nii/status.json"
        if os.path.exists(nii):
            with open(nii) as data_file:
                data = json.load(data_file)
                json.dump(data)



                if len(data["t1_files"]) > 0:
                    seq = data["t1_files"]
                    for reorient in seq:
                        if "reorient" in reorient:
                            print(reorient)
                            print(data)
                            print("******")
                            print(data_file, reorient)
                            json.dump(data_file, reorient)





def get_align(mse):
    t1_file = ""
    try:
        align = _get_output(mse)+"/"+mse+"/alignment/status.json"
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"]
        return t1_file
    except:
        pass

def check_int(t1):
    cmd = ["fslstats", t1, "-R" ]
    proc = Popen(cmd, stdout=PIPE)
    max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
    #print(max)
    check = ""
    if max.endswith(".0"):
        #print(max, "True")
        check = True
    else:
        check = False
        #print(max, "False")
    return check


def get_t1(mse):
    t1_file = ""
    if mse.startswith("mse"):
        get_align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
        if os.path.exists(get_align):
            with open(get_align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1].replace("_reorient", "")
                    if "DESPOT" in t1_file:
                        cmd = ["pbr", mse, "-w", "align","-R"]
                        #Popen(cmd).wait()
                        t1_file = data["t1_files"][0].replace("_reorient", "")
    return t1_file

def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
        date = str(df.loc[idx, 'date']).split(".0")[0]
        mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
        mse2 = "mse" + str(df.loc[idx, 'mse2']).replace("mse", "").lstrip("0")
        pbvc = df.loc[idx, "pbvc"]
        henry12 =  "/data/henry12/PBR_long/subjects/"
        henry10 = "/data/henry10/PBR_long/subjects/"
        output =  henry10 + msid + '/siena_optibet/' + mse +"__"+ mse2
        sienax = df.loc[idx, 'sienax']
        #rerun = df.loc[idx, 'siena_rerun']
        lesion_orig = "{}/{}/lesion_origspace_flair/lesion.nii.gz".format(_get_output(mse), mse)
        sienax_out =  "{}/{}/sienaxorig_flair/".format(_get_output(mse), mse)
        #mse1_t1 = get_t1(mse)
        #mse2_t1 = get_t1(mse2)
        """try:
            mse1_t1 = get_t1(mse)
            mse2_t1 = get_t1(mse2)
            if len(str(pbvc)) < 4: #"rerun":
                #print(pbvc)
                if os.path.exists(mse1_t1) and os.path.exists(mse2_t1):
                    if not os.path.exists(output):
                        #print("removing", output)
                        #shutil.rmtree(output)
                    #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
                        print("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output)
                        cmd = ["siena_optibet", get_t1(mse), get_t1(mse2), "-o", output]
                        Popen(cmd).wait()
        except:
            pass"""


        """try:
            if mse.startswith("mse") and mse2.startswith("mse"):
                #if os.path.exists(mse1_t1) and os.path.exists(mse2_t1):
                if not os.path.exists(output + '/report.siena') and not os.path.exists("{}/{}/siena_optibet/{}__{}".format(henry12),msid,mse, mse2):
                        print("{}/{}/siena_optibet/{}__{}".format(henry10),msid,mse, mse2)
                        print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
                else:

                            sienaA = glob("/data/henry*/PBR_long/subjects/{0}/siena_optibet/{1}*{2}*/A.nii.gz".format(msid, mse, mse2))[0]
                            sienaB = glob("/data/henry*/PBR_long/subjects/{0}/siena_optibet/{1}*{2}*/B.nii.gz".format(msid, mse, mse2))[0]

                            ca =  "/data/henry6/gina/siena_check/"+ mse + "A.nii.gz"
                            ba = "/data/henry6/gina/siena_check/"+ mse + "B.nii.gz"
                            if not os.path.exists(ca) and not os.path.exists(ba):
                                shutil.copyfile(sienaA, ca)
                                shutil.copyfile(sienaB, ba)
                                checkA = check_int(ca)
                                checkB = check_int(ba)
                                if checkA == False or checkB == False:
                                    print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
        except:
            pass

                    #cmd = ["siena_optibet", get_t1(mse), get_t1(mse2), "-o", output]
                    #Popen(cmd).wait()
        if mse.startswith("mse") and mse2.startswith("mse"):
            #print(mse, mse2)
            try:
                if os.path.exists(mse1_t1) and os.path.exists(mse2_t1):
                    check1 = check_int(mse1_t1)
                    check2 = check_int(mse2_t1)

                    if check1 == False:
                        run_nifti_align(mse)
                    if check2 == False:
                        run_nifti_align(mse2)
            except:
                pass

        if sienax == "False":
            txt = "/data/henry6/gina/epic_text/" + msid + ".txt"
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", txt, "-w", "t1MNI_long","-R"))
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", txt, "-w", "FLAIRles_long","-R"))
            print("pbr", txt, "-w","t1MNI_long", "FLAIRles_long","-R")
            cmd = ["pbr", txt, "-w", "t1MNI_long","-R"]
            Popen(cmd).wait()
            cmd = ["pbr", txt, "-w", "FLAIRles_long","-R"]
            Popen(cmd).wait()




        if os.path.exists(lesion_orig) and not os.path.exists(sienax_out):
            #print("")
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", mse, "-w", "sienax_optibet", "-R"))
            print("pbr", mse, "-w","sienax_optibet", "-R")
            cmd = ["pbr", mse, "-w","sienax_optibet", "-R"]
            Popen(cmd).wait()



        if sienax == "False":
            txt = "/data/henry6/gina/epic_text/" + msid + ".txt"
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", txt, "-w", "t1MNI_long","-R"))
            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", txt, "-w", "FLAIRles_long","-R"))
            print("pbr", txt, "-w", "FLAIRles_long","-R")
            cmd = ["pbr", txt, "-w", "FLAIRles_long","-R"]
            Popen(cmd).wait()

        try:
            mse1_t1 = get_t1(mse)
            mse2_t1 = get_t1(mse2)
            if len(str(pbvc)) < 4:
                #print(pbvc)
                if os.path.exists(mse1_t1) and os.path.exists(mse2_t1):
                    print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
        except:
            pass
        #resample = df.loc[idx, "resample_sienax"]
        #pbvc = df.loc[idx, "pbvc"]


        #if mse.startswith("mse") and mse2.startswith("mse") and not mse2.endswith("nan"):
            #print(mse, mse2)




            #if len(str(pbvc)) < 4 or pbvc == 2:
                #print(str(pbvc))
                #print("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output)

                #print(mse,mse2)
                siena_old =output.replace("henry12","henry10")
                #if os.path.exists(siena_old):
                    #os.rmtree(output.replace("henry12","henry10"))
                    #if len(mse) > 4 and len(mse2) > 4:
                        #if not os.path.exists(output + '/report.siena'):
                            #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
                            #print("")
                #cmd = ["siena_optibet", get_t1(mse), get_t1(mse2), "-o", output]
                #Popen(cmd).wait()
        except:
            pass


            try:
                #henry10 = glob("/data/henry10/PBR_long/subjects/{}/siena_optibet/{}".format(msid, mse, mse2) + msid + "/" + mse + "__" + mse2)
                if not os.path.exists("/data/henry10/PBR_long/subjects/" + msid + "/siena_optibet/" + mse + "__" + mse2 + '/report.siena' ):
                    #print(output)
                    if not os.path.exists(output + '/report.siena'):
                        #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("siena_optibet", get_t1(mse), get_t1(mse2), "-o", output))
                        if os.path.exists(get_t1(mse)) and os.path.exists(get_t1(mse2)):
                            if not os.path.exists(henry12 + msid):
                                os.mkdir(henry12 + msid)
                            if not os.path.exists(henry12 + msid + '/siena_optibet/'):
                                os.mkdir(henry12 + msid + '/siena_optibet/')
                            print("siena_optibet", get_t1(mse), get_t1(mse2), "-o", -output)
                            #cmd = ["siena_optibet", get_t1(mse), get_t1(mse2), "-o", output]
                            #Popen(cmd).wait
            except:
                pass
            if str(resample) == "False":
                #run_nifti_align(mse)
                lesion_orig = "{}/{}/lesion_origspace_flair/lesion.nii.gz".format(_get_output(mse), mse)
                if os.path.exists(lesion_orig):
                    print("")
                    #print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", mse, "-w", "sienax_optibet", "-R"))
                    #cmd = ["pbr", mse, "-w","sienax_optibet", "-R"]
                    #Popen(cmd).wait()
                else:
                    print("pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "t1MNI_long", "FLAIRles_long", "-R")
                    cmd = ["pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "t1MNI_long", "-R"]
                    Popen(cmd).wait()
                    cmd = ["pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "FLAIRles_long", "-R"]
                    Popen(cmd).wait()
            if len(str(vscale)) < 4:
                print(vscale)
                print("pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "t1MNI_long", "FLAIRles_long", "-R")
                cmd = ["pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "t1MNI_long", "-R"]
                Popen(cmd).wait()
                cmd = ["pbr", "/data/henry6/gina/epic_text/"+ msid + ".txt", "-w", "FLAIRles_long", "-R"]
                Popen(cmd).wait()"""



        if mse.startswith("mse"):
            if not os.path.exists(_get_output(mse) + "/" + mse + "/first_all/"):
                print("python", "/data/henry6/gina/scripts/grid_submit.py", '"{} {} {} {} {}"'.format("pbr", mse, "-w", "first_all", "-R") )
                #print("pbr", mse, "-w", "first_all", "-R")
                #cmd = ["pbr-sge", "-s", mse,"-w", '"{} {} {}"'.format("-w", "first_all", "-R")]
                #print("pbr-sge", "-s", mse, '"{} {} {}"'.format("-w", "first_all", "-R"))
                #cmd = ["pbr", mse, "-w", "first_all", "-R"]
                #Popen(cmd).wait()
            #else:
                #print(mse, "first exists")"


                    
            #check_json(mse)
            #edit_json(mse)

            """print(mse)
            t1 = get_align(mse)
            for T1 in t1:
                print(T1)
                check = ""
                try:
                    check = check_int(T1)
                except:
                    check = "False"
                df.loc[idx, 'resampling'] = check"""



    #df.to_csv(out)


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
