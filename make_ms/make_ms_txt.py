import pbr
import os
from nipype.utils.filemanip import load_json
from pbr.workflows.nifti_conversion.utils import description_renamer
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
import pandas as pd
from subprocess import Popen, PIPE
import pandas as pd
import argparse


def get_all_mse(msid):
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.split("ms")[1]]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    print(lines)
    tmp = pd.DataFrame(lines, columns=["mse", "dates"])
    tmp["mse"] = "mse"+tmp.mse
    tmp["msid"] = msid
    return tmp

def get_modality(mse, nii_type="T1"):
    output = pd.DataFrame()
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    if nii_type:
        files = filter_files(lines, nii_type, heuristic)
        output["nii"] = files
        try:
            files[0]
            with open(out_file, "a") as text_file:
                text_file.write(mse + "\n")
        except:

            pass
    else:
        output["nii"] = lines
    output["mse"] = mse

    return output

def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument('-o', help = 'output directory')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    df = pd.read_csv("{}".format(c))
    msID = df['msid'].iloc[0]
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        output = out + msID + ".txt"
        with open(output, "a") as text_file: 
            text_file.write(mse + "\n")
        if msid == msID:
            
        else:
            msID = msid
            output = out + msid + ".txt" 



"""if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code creates an text file of mses given an msid')
    parser.add_argument('-i', help = 'csv containing the msid')
    parser.add_argument('-o', help = 'output directory')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        msid = row['msid']
        ms = row["msid"]
        print(msid)
        out_file = out + ms +'.txt'
        print(out_file)
        mse_df = get_all_mse(msid)
        print(mse_df.mse)
        for mse in mse_df.mse:
            get_modality(mse, "T1")"""




