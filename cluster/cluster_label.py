import numpy as np
import os
import nibabel as nb
from collections import defaultdict
image_path= "/data/henry7/PBR/subjects/mse3217/ms1489-mse3217-004-BRAVO_IRSPGR_fa8_ti600_reorient_semi.nii.gz"
image=nb.load(image_path)
imall=image.get_data()
sh=imall.shape
num=0
tabl=defaultdict(int)
def has_adjacent(i,j):
	r_list=[]
	try:
		if im[i-1,j+1]!=0 and tabl[(i-1,j+1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i-1,j+1))
	except:
		pass
		
	try:
		if im[i,j+1]!=0 and tabl[(i,j+1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i,j+1))
	except:
		pass
		
	try:
		if im[i+1,j+1]!=0 and tabl[(i+1,j+1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i+1,j+1))
	except:
		pass
		
	try:
		if im[i+1,j]!=0 and tabl[(i+1,j)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i+1,j))
	except:
		pass
	try:
		if im[i+1,j-1]!=0 and tabl[(i+1,j-1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i+1,j-1))
	except:
		pass
	try:
		if im[i,j-1]!=0 and tabl[(i,j-1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i,j-1))
	except:
		pass
	try:
		if im[i-1,j-1]!=0 and tabl[(i-1,j-1)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i-1,j-1))
	except:
	        pass
	try:
		if im[i-1,j]!=0 and tabl[(i-1,j)]==0 and abs(i)==i and abs(j)==j:
			r_list.append((i-1,j))
	except:
		pass
	return r_list
def cluster_find(i,j,num):
	#recursive function
	global tabl
	#print('first {}:{}'.format(i,j))
	if  im[i,j]==0 or tabl[(i,j)] or abs(i)!=i or abs(j)!=j:
		return
	else:
		#print('{}:{}'.format(i,j))
		tabl[(i,j)]=num
		for kernel in has_adjacent(i,j):
			cluster_find(kernel[0],kernel[1],num)
def lesion_fill(cluster_num,im):
	for i in cluster_num:
		
		lesion=sorted(cluster_num[i],key=lambda x:x[0])
		lesion=sorted(lesion,key=lambda x:x[1])
		line_dict=defaultdict(list)
		for j in lesion:
			line_dict[j[1]].append(j)
		for k in line_dict:
			#print(line_dict[k])
			#input('line_dict')
			for filler in range(line_dict[k][-1][0]-line_dict[k][0][0]):
				#print(filler)
				im[filler+line_dict[k][0][0],k]=1
	return im

#2d lesion finding/labeling and filling
for x in range(sh[2]):
	tabl=defaultdict(int)
	im=imall[:,:,x]	
	for i in range(sh[0]):
		for j in range(sh[1]):
			if im[i,j]==0 or tabl[(i,j)]:
				continue
			num=num+1
			#print('{}:{}'.format(i,j))
			cluster_find(i,j,num)
	clusters=defaultdict(int)
	cluster_num=defaultdict(list)
	for coords in tabl:
		clusters[tabl[coords]]+=1
		cluster_num[tabl[coords]].append(coords)
		#im[coords[0],coords[1]]=tabl[coords]
	imall[:,:,x]=lesion_fill(cluster_num,im)

nb.save(nb.Nifti1Image(imall,image.affine), "/data/henry7/PBR/subjects/mse3217/ms1489-mse3217-004-BRAVO_IRSPGR_fa8_ti600_reorient_lesion.nii.gz")
   #'/data/henry10/jjuwono/filled'+os.path.basename(image_path))
#csf=np.where(im==greatest[1],im,0)
#print(com.center_of_mass(csf,image.affine))
	#for each iteration num+1
	#after every iteration the clsuter corresponding to that iteration shoudlbe found
