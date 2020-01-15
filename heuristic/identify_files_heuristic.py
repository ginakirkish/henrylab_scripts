import pbr
import os
from subprocess import Popen, PIPE
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import argparse

def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output

def get_modality(mse):
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num, "-D"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    sequences  = ["T2_spine"]
    for sq in sequences:
        print("checking for...", sq)
        nii_type = sq
        if nii_type:
            series_name = filter_files(lines, nii_type, heuristic)
            if len(series_name)>0:
                series_name = series_name[0]
                print(series_name, " is the {0}".format(sq))
            else:
                print(mse, "No {0} in dicom identified by the heuristic...Please check sequnces and heuristic".format(sq))



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code checks for C1 C2 images')
    parser = argparse.ArgumentParser()
    parser.add_argument("mse")
    args = parser.parse_args()
    get_modality(args.mse)

