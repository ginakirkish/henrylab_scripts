from pbr.base import _get_output
from os.path import join
from nipype.utils.filemanip import load_json
import nibabel as nib
import numpy as np
from nipype.interfaces import fsl
import nipype.pipeline.engine as pe
from nipype.pipeline.engine import  Workflow, Node
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import DataSink
from nipype.utils.filemanip import load_json
from os.path import join, exists
from pbr.base import _get_output

def reorient2std(in_file):
    ''' returns the affine from the fslreorient2std command'''

    from subprocess import Popen, PIPE
    from os import getcwd

    wd = getcwd()

    cmd = ['fslreorient2std', in_file]
    p = Popen(cmd, stdout=PIPE)
    p.wait()

    out_file = '{}/reo2std.txt'.format(wd)
    with open(out_file, 'w') as f:
        for line in p.stdout.readlines()[:-1]:
            line = line.decode('utf-8')
            f.write(line)

    return out_file

def reverse_robustFOV_func(in_file, reference, in_matrix):
    """ This applies the inverse of the robustFOV function"""

    import nibabel as nib
    import numpy as np
    from os import getcwd


    wd = getcwd()

    ref_shape = nib.load(reference).get_data().shape
    img = nib.load(in_file).get_data()
    aff = nib.load(in_file).affine

    zeros = np.zeros(ref_shape)

#     zeros[int(ref_shape[0]-img.shape[0]):, int(ref_shape[1]-img.shape[1]):, int(ref_shape[2] -img.shape[2]):] = img

    zeros[:img.shape[0], :img.shape[1], :img.shape[2]] = img
    out_file = '{}/reverse_FOV.nii.gz'.format(wd)
    print(out_file)
    nib.save(nib.Nifti1Image(zeros, aff), out_file)

    return out_file

def binarize(in_file):
    """ Binarize the lesion mask after being transformed"""

    import nibabel as nib
    import numpy as np
    from os import getcwd
    from scipy.ndimage.morphology import binary_closing

    wd = getcwd()

    img, aff = nib.load(in_file).get_data(), nib.load(in_file).affine

    # binarize
    img[np.where(img != 0)] = 1

    # close
    img[binary_closing(img)] = 1

    out_file = '{}/lesion_mask_binarized.nii.gz'.format(wd)
    print('Saving binarized img at {}'.format(out_file))
    nib.save(nib.Nifti1Image(img, aff), out_file)

    return out_file

def run_align2nii(mseid, nifti, lesion_mask, out_directory):

    wf = Workflow(name='{}_align2nii'.format(mseid), base_dir = '/working/henry_temp/keshavan/')

    inputspec = pe.Node(IdentityInterface(fields=['nii_img', 'lesion_mask', 'mseid']), name='inputspec')
    inputspec.inputs.mseid = mseid
    inputspec.inputs.nii_img = nifti
    inputspec.inputs.lesion_mask = lesion_mask

    # find robustFOV transformation for nifti image
    nifti_robust = pe.Node(fsl.RobustFOV(), name='nifti_robust')
    wf.connect(inputspec, 'nii_img', nifti_robust, 'in_file')

    # reo2std img into standard space
    nifti_reo2std = pe.Node(Function(input_names=['in_file'], output_names=['out_file'],
                                     function=reorient2std),
                            name='nifti_reo2std')
    wf.connect(nifti_robust, 'out_roi', nifti_reo2std, 'in_file')

    # convert robustFOV mat to inverse
    robustFOV_inv = pe.Node(fsl.ConvertXFM(), name='robustFOV_inv')
    robustFOV_inv.inputs.invert_xfm = True
    wf.connect(nifti_robust, 'out_transform', robustFOV_inv, 'in_file')

    # convert reo2std mat to inverse
    reo2std_inv = pe.Node(fsl.ConvertXFM(), name='reo2std_inv')
    reo2std_inv.inputs.invert_xfm = True
    wf.connect(nifti_reo2std, 'out_file', reo2std_inv, 'in_file')


    # apply xfm from reo2std of nifti image to the lesion mask
    apply_reo2std_xfm = pe.Node(fsl.FLIRT(), name ='apply_reo2std_inverse_xfm')
    apply_reo2std_xfm.inputs.apply_xfm = True
    wf.connect(reo2std_inv, 'out_file', apply_reo2std_xfm, 'in_matrix_file')
    wf.connect(inputspec, 'lesion_mask', apply_reo2std_xfm, 'in_file')
    wf.connect(nifti_robust, 'out_roi', apply_reo2std_xfm, 'reference')

    # reverse robustFOV from nifti image
    reverse_robustFOV = pe.Node(Function(input_names=['in_file', 'reference', 'in_matrix'], output_names=['out_file'],
                                        function=reverse_robustFOV_func),
                               name='reverse_robustFOV')
    wf.connect(nifti_robust, 'out_transform', reverse_robustFOV, 'in_matrix')
    wf.connect(apply_reo2std_xfm, 'out_file', reverse_robustFOV, 'in_file')
    wf.connect(inputspec, 'nii_img', reverse_robustFOV, 'reference')


    # apply xfm from robustFOV of nifti image to the Lesion mask
    apply_nifti_robust_xfm = pe.Node(fsl.FLIRT(), name='apply_nifti_robust_xfm')
    apply_nifti_robust_xfm.inputs.apply_xfm = True
    wf.connect(reverse_robustFOV, 'out_file', apply_nifti_robust_xfm, 'in_file')
    wf.connect(inputspec, 'nii_img', apply_nifti_robust_xfm, 'reference')
    wf.connect(nifti_robust, 'out_transform', apply_nifti_robust_xfm, 'in_matrix_file')
#     wf.connect(robustFOV_inv, 'out_file', apply_nifti_robust_xfm, 'in_matrix_file')

    # binarize lesion mask
    binarizer = pe.Node(Function(input_names=['in_file'], output_names=['out_file'],
                                function=binarize),
                       name='binarize_lesion_mask')
    wf.connect(apply_nifti_robust_xfm, 'out_file', binarizer, 'in_file')

    # data sink
    sink = pe.Node(DataSink(), name='sinker')
    sink.inputs.base_directory = out_directory
    wf.connect(binarizer, 'out_file', sink, '@binarizer')


    wf.run()

with open('/data/henry6/gina/mse/test_mse.txt', 'r') as f:
    mseid_list = [x.strip() for x in f.readlines()]

print(mseid_list)


error_list = []
wf_fail = []

for mseid in mseid_list:
    nifti_img = max(load_json(join(_get_output(mseid), mseid, 'nii', 'status.json'))['t1_files'])
    lesion_mask = join(_get_output(mseid), mseid, 'lesion_origspace_flair', 'lesion.nii.gz')

    if not exists(lesion_mask):
        error_list.append(mseid)
        continue

    try:
        run_align2nii(mseid, nifti_img, lesion_mask, join(_get_output(mseid), mseid, 'lesions'))
    except:
        wf_fail.append(mseid)

print('\nCompleted with these imgs not having lesion masks {}\nAnd these images not being able to run WF{}'.format(error_list,wf_fail))
