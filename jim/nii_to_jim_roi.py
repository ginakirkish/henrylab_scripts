import nibabel as nib
import numpy as np
import scipy.ndimage.interpolation as wezoom
import glob
import os
import sys
import argparse
import copy

def load(image):
    img = nib.load(image)
    img_header = img.get_header()
    img_affine = img.get_affine()
    img_data = np.array(img.get_data())
    return img_affine, img_data, img_header

def getpts(nii):

    nii_aff, nii_data, nii_header = load(nii)
    nii_coords = []
    for z in range(nii_data.shape[2]):
        x,y = np.where(nii_data[:, :, z] == 1)
        if x.size:
            coord = [x[0], y[0], z]
            print('point found at', coord) 
            nii_coords.append(coord)
    return nii_coords
 
def nii2jim(nii_coords, img_shape, voxdims):
    jim_coords = copy.deepcopy(nii_coords)
    for slice_num in range(len(nii_coords)):
        jim_coords[slice_num][0] = (nii_coords[slice_num][0]- img_shape[0]/2.0) * voxdims[0]/1.0  
        jim_coords[slice_num][1] = (img_shape[1]/2.0 - nii_coords[slice_num][1]) * voxdims[1]/1.0 
    return jim_coords
 
def make_roi(coords, roi, img, out_roi): 
    roifile = open(roi, 'r')
    lines = roifile.readlines()
    shape_num = 0
    for idx,line in enumerate(lines):
        if 'Slice=' in line:
            print('idx', idx)
            print('lines idx', lines[idx])
            print('len of coords', len(coords), 'shape num', shape_num)
            lines[idx] = 'Slice={}\n'.format(str(coords[shape_num][2]+1)) #Makes this line now the z coord from nii 
        if 'Begin Shape' in line:
            shape_num += 1
        if 'X=' in line:
            lines[idx] = '    X={}; Y={}\n'.format(str(coords[shape_num-1][0]), str(coords[shape_num-1][1])) 
        if 'Image source' in line:
            lines[idx] = 'Image source="{}"'.format(img)
        if 'End Marker' in line and shape_num == len(coords):
            lines = lines[:idx+1]
            break
    roifile.close()
    
    print('saving roi file at', out_roi)
    with open(out_roi, 'w') as file:
        file.writelines(lines)

def nii_to_jim(nii, img, out, roi):
    nii_coords = getpts(nii)
    img_aff, img_data, img_hdr = load(img)
    vox_dims = img_hdr.get_zooms()
    jim_coords = nii2jim(nii_coords, img_data.shape, vox_dims) 
    make_roi(jim_coords, roi, img, out) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This script converts from nifti file to jim.roi file, however it requires a template roi file to exist. It essentially overwrites the original roi file with the new data that is passed via the nifti file')
    parser.add_argument('-roi', help='input roi file')
    parser.add_argument('-nii', help='nii file to convert')
    parser.add_argument('-img', help='image nii file used to create roi')
    parser.add_argument('-out', help='location of output roi file')
    args = parser.parse_args()
    nii_to_jim(args.nii, args.img, args.out, args.roi)
