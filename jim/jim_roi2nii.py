#!/usr/bin/env python
from matplotlib.path import Path
import copy
import nibabel as nib
import numpy as np
import glob
import os
import sys
import argparse

def create_nifti_file(img, roi):

    # settings
    k1, line, shape_num = getpts(roi)
    print('k1', k1)
    img_affine, img_data, img_header = load(img)
    img_shape = img_data.shape
    voxdims = img_header.get_zooms()
    print('vox dims', voxdims)

    a1=np.ones([k1.shape[0],k1.shape[1]])
    a1[:,1]=-1
    k1flip = k1*a1
    print('k1flip', k1flip)
   
    if line.size:
        l_a1=np.ones([line.shape[0],line.shape[1]])
        l_a1[:,1]=-1
        line_flip = line*l_a1
        print('line_flip', line_flip)
    else:
        line_flip = line
    
    # TRANSFORM FROM JIM COORDINATES (0,0 at center of JIM image) TO NIFTI SPACE
    k1_new = jim2psir(k1flip, line_flip, img_shape, voxdims)
    print('k1_new', k1_new)
    print('k1_new[:,1]', k1_new[:, 1])
    print('k1_new[:,0]', k1_new[:, 0])

    # MAKE NIFTI FILE
    nifti = make_nifti(img_data, k1_new, shape_num)
    
    return nifti, img_affine

def save_image(file_data, file_affine, file_name):
    image = nib.Nifti1Image(file_data, file_affine)
    print('dataype of image to save', type(image))
    print('saving nii image as', file_name)
    image.to_filename(file_name)
    return

def getpts(filepath):
    rois = 0
    slice_num = 0
    marker_array=[]
    line_array = []
    cordlist = []
    linelist = []
    roifile = open(filepath, 'r')
    lines = roifile.readlines()
    roifile.close()
    shape_num = 0
    for line in lines:
        if "Deleted" in line:
            print('This Jim file has been overwritten, now stopping scraping JIM file for data')
            break
        if "Slice=" in line:
            slice_num = line[8:-1]
        if "Begin Shape" in line:
            shape_num = shape_num+1
        if "X=" in line:
            cordlist.append(line.strip()+'; Z='+str(slice_num)+'; S='+str(shape_num))
        if "X1=" in line:
            linelist.append(line.strip()+'; Z='+str(slice_num)+'; S='+str(shape_num))
    for pt in cordlist:
        parts = pt.split('=')
        x = parts[1][:-3]
        y = parts[2][:-3]
        z = parts[3][:-3]
        s = parts[4]
        marker_array.append([x, y, z, s])
    marker_array = np.array(marker_array, dtype='float64')
    for pt in linelist: 
        parts = pt.split('=')
        x1 = parts[1][:-4]
        y1 = parts[2][:-4]
        x2 = parts[3][:-4]
        y2 = parts[4][:-3]
        z = parts[5][:-3]
        s = parts[6]
        line_array.append([x1, y1, z, s])
        line_array.append([x2, y2, z, s])
    line_array = np.array(line_array, dtype = 'float64')
    return marker_array, line_array, shape_num

def load(image):
    img = nib.load(image)
    img_header = img.get_header()
    img_affine = img.get_affine()
    img_data = np.array(img.get_data())
    return img_affine, img_data, img_header

def jim2psir(k1flip, line, img_shape, voxdims): 

    k1_new = k1flip
    k1_new[:,0] = k1flip[:,0]*(1.0/voxdims[0])+img_shape[0]/2.0
    k1_new[:,1] = k1flip[:,1]*(1.0/voxdims[1])+img_shape[1]/2.0
 
    #Code turn the .roi line information into a nifti
    if line.size:
        line_new = copy.deepcopy(line)
        out_line_array = []
        line_new[:,0] = line[:,0]*(1.0/voxdims[0])+img_shape[0]/2.0
        line_new[:,1] = line[:,1]*(1.0/voxdims[0])+img_shape[1]/2.0
        print('line new', line_new)
        for idx in range(2 , len(line_new)+2, 2):
            line_pts = line_new[idx-2:idx]
            print('line_pts', line_pts)
            if len(np.unique(line_pts[:,0])) != 1:
                print('Generating line for x axis for pts \n {}'.format(line_pts))
                x_min = min(line_pts[:,0])
                x_max = max(line_pts[:,0]) 
                y_val = np.unique(line_pts[:,1])[0]
                z_val = np.unique(line_pts[:,2])[0]
                s_val = np.unique(line_pts[:3])[0]
                for x in range(int(x_min)+1, int(x_max)):
                    line_new = np.vstack((line_new,[x, y_val, z_val, s_val]))
            if len(np.unique(line_pts[:,1])) != 1:
                print('Generating line for y axis for pts \n {}'.format(line_pts))
                y_min = min(line_pts[:,1])
                y_max = max(line_pts[:,1]) 
                x_val = np.unique(line_pts[:,0])[0]
                z_val = np.unique(line_pts[:,2])[0]
                s_val = np.unique(line_pts[:3])[0]
                for y in range(int(y_min)+1, int(y_max)):
                    line_new = np.vstack((line_new,[x_val, y, z_val, s_val]))
        output_array = np.vstack((k1_new, line_new)) 
    else:
        output_array = k1_new    
    #k1_new = k1flip*1.28+128
    #print('integer converted coordinates', k1_new.astype(int))
    return output_array

def make_nifti(img_data, k1flip, shape_num):
    nifti = np.zeros(np.shape(img_data))
    for s in range(1,shape_num+1):
        print('making nifti for shape 1')
        k1_slice_shape = k1flip[k1flip[:,3] == s]
        z = int(k1_slice_shape[0,2]) -1 # subtracted one here but not sure if it is correct LOL
        k1_slice_shape = k1_slice_shape[:,:-2]
        k1flip_path = Path(k1_slice_shape)
        for slice_shp in k1_slice_shape:
            x = int(slice_shp[0])
            y = int(slice_shp[1])
            nifti[x,y,z] = 1
                
    return nifti

def jim_to_nii(roi, img, output):
    nifti, affine = create_nifti_file(img, roi)
    save_image(nifti, affine, output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('This script converts from Jim .roi file to nifti...hopefully')
    parser.add_argument("-roi", help="roi file created with Jim")
    parser.add_argument("-img", help="image nii file used to create roi")
    parser.add_argument("-output", help="location of output nii file")
    args = parser.parse_args()
    jim_to_nii(args.roi, args.img, args.output)
