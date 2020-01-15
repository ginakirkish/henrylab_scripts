#!/bin/sh

#   sienax - Structural Image Evaluation, including Normalisation, of Atrophy (X-sectional)
#
#   Stephen Smith, FMRIB Image Analysis Group
#
#   Copyright (C) 1999-2007 University of Oxford
#
#   Part of FSL - FMRIB's Software Library
#   http://www.fmrib.ox.ac.uk/fsl
#   fsl@fmrib.ox.ac.uk
#
#   Developed at FMRIB (Oxford Centre for Functional Magnetic Resonance
#   Imaging of the Brain), Department of Clinical Neurology, Oxford
#   University, Oxford, UK
#
#
#   LICENCE
#
#   FMRIB Software Library, Release 4.0 (c) 2007, The University of
#   Oxford (the "Software")
#
#   The Software remains the property of the University of Oxford ("the
#   University").
#
#   The Software is distributed "AS IS" under this Licence solely for
#   non-commercial use in the hope that it will be useful, but in order
#   that the University as a charitable foundation protects its assets for
#   the benefit of its educational and research purposes, the University
#   makes clear that no condition is made or to be implied, nor is any
#   warranty given or to be implied, as to the accuracy of the Software,
#   or that it will be suitable for any particular purpose or for use
#   under any specific conditions. Furthermore, the University disclaims
#   all responsibility for the use which is made of the Software. It
#   further disclaims any liability for the outcomes arising from using
#   the Software.
#
#   The Licensee agrees to indemnify the University and hold the
#   University harmless from and against any and all claims, damages and
#   liabilities asserted by third parties (including claims for
#   negligence) which arise directly or indirectly from the use of the
#   Software or the sale of any products based on the Software.
#
#   No part of the Software may be reproduced, modified, transmitted or
#   transferred in any form or by any means, electronic or mechanical,
#   without the express permission of the University. The permission of
#   the University is not required if the said reproduction, modification,
#   transmission or transference is done without financial return, the
#   conditions of this Licence are imposed upon the receiver of the
#   product, and all original and amended source code is included in any
#   transmitted product. You may be held legally responsible for any
#   copyright infringement that is caused or encouraged by your failure to
#   abide by these terms and conditions.
#
#   You are not permitted under this Licence to use this Software
#   commercially. Use for which any financial return is received shall be
#   defined as commercial use, and includes (1) integration of all or part
#   of the source code or the Software into a product for sale or license
#   by or on behalf of Licensee to third parties or (2) use of the
#   Software or any derivative of it for research with the final aim of
#   developing software products for sale or license to a third party or
#   (3) use of the Software or any derivative of it for research with the
#   final aim of developing non-software products for sale or license to a
#   third party, or (4) use of the Software to provide any service to an
#   external organisation for which payment is received. If you are
#   interested in using the Software commercially, please contact Isis
#   Innovation Limited ("Isis"), the technology transfer company of the
#   University, to negotiate a licence. Contact details are:
#   innovation@isis.ox.ac.uk quoting reference DE/1112.

Usage() {
    cat <<EOF

Usage: sienax <input> [options]

  -o <output-dir> : set output directory (default output is <input>_sienax)
  -d              : debug (don't delete intermediate files)
  -B "betopts"    : options to pass to optiBET brain extraction (inside double-quotes), e.g. -B "-d -f 0.1"
  -2              : two-class segmentation (don't segment grey and white matter separately)
  -t2             : T2-weighted input image (default T1-weighted)
  -t <t>          : ignore from t (mm) upwards in MNI152/Talairach space
  -b <b>          : ignore from b (mm) downwards in MNI152/Talairach space (b should probably be negative)
  -r              : regional - use standard-space masks to give peripheral cortex GM volume (3-class segmentation only) and ventricular CSF volume
  -lm <mask>      : use lesion (or lesion+CSF) mask to remove incorrectly labelled "grey matter" voxels
  -lt             : specify the type of lesion mask used
  -S "segopts"    : options to pass to FAST segmentation (inside double-quotes), e.g. -S "I 20"

EOF
    exit 1
}


[ _$1 = _ ] && Usage
fname=$(pwd)'/'$1
a=`echo $1 | cut -c1-1`
if [ "$a" == "/" ] ; then
    fname=$1
fi

Io=`${FSLDIR}/bin/remove_ext $1`;
[ `${FSLDIR}/bin/imtest ${Io}` = 0 ] && Usage
thecommand="sienax_MONSTR $@"
shift

outdir=${Io}_sienax
debug=0
regional=0
betopts=""
segopts=""
nseg=3
stdroi=""
origin3=37 # `fslval ${FSLDIR}/data/standard/MNI152_T1_2mm origin3`
pixdim3=2  # `fslval ${FSLDIR}/data/standard/MNI152_T1_2mm pixdim3`
imtype="-t 1"

while [ _$1 != _ ] ; do

    if [ $1 = -d ] ; then
        debug=1
        shift
    elif [ $1 = -o ] ; then
        outdir=$2
        shift 2
    elif [ $1 = -r ] ; then
	regional=1
        shift
    elif [ $1 = -B ] ; then
        betopts=$2
        shift 2
    elif [ $1 = -S ] ; then
        segopts=$2
        shift 2
    elif [ $1 = -2 ] ; then
        nseg=2
        shift
    elif [ $1 = -t2 ] ; then
        imtype="-t 2"
        shift
    elif [ $1 = -t ] ; then
	stdt=`echo $2 | sed 's/-/_/g'`
	stdt=`echo "10 k $stdt $pixdim3 / $origin3 + p" | dc -`
	stdroi="$stdroi -roi 0 1000000 0 1000000 0 $stdt 0 1"
	shift 2
    elif [ $1 = -b ] ; then
	stdb=`echo $2 | sed 's/-/_/g'`
	stdb=`echo "10 k $stdb $pixdim3 / $origin3 + p" | dc -`
	stdroi="$stdroi -roi 0 1000000 0 1000000 $stdb 1000000 0 1"
	shift 2
    elif [ $1 = -lm ] ; then
	lm=$2
	shift 2
	elif [ $1 = -lt ] ; then
    lt=$2
    shift 2
    else
	Usage
    fi

done

if [ $regional = 1 ] ; then
    if [ $nseg = 2 ] ; then
	echo "Can't do regional analysis with 2-class segmentation"
	exit
    fi
fi

mkdir -p $outdir
${FSLDIR}/bin/imcp $Io ${outdir}/I
if [ _$lm != _ ] ; then
    ${FSLDIR}/bin/imcp $lm ${outdir}/lesion_mask_$lt
    lm=lesion_mask_$lt
fi
cd $outdir
I=I
echo "$fname" >> filename.sienax
echo "$thecommand" >> command.sienax
echo '<HTML><HEAD><link REL="stylesheet" TYPE="text/css" href="file:'${FSLDIR}'/doc/fsl.css"><TITLE>FSL</TITLE></HEAD><BODY><hr><TABLE BORDER=0 WIDTH="100%"><TR><TD ALIGN=CENTER><H1>SIENAX Report</H1>'${thecommand}'<TD ALIGN=RIGHT><a href="'${FSLDIR}'/doc/index.html"><IMG BORDER=0 SRC="'${FSLDIR}'/doc//images/fsl-logo.jpg"></a></TR></TABLE>' > report.html


echo "-----------------------------------------------------------------------" >  report.sienax
echo ""                                                                        >> report.sienax
echo " SIENA - Structural Image Evaluation, using Normalisation, of Atrophy"   >> report.sienax
echo " part of FSL www.fmrib.ox.ac.uk/fsl"                                     >> report.sienax
echo " running cross-sectional atrophy measurement: sienax version 2.6"        >> report.sienax
echo " sienax $@"                                                              >> report.sienax
echo "INPUTIMG $Io"                                                            >> report.sienax
echo ""                                                                        >> report.sienax

echo "----------  extract brain with MONSTR --------------------------------------------" >> report.sienax
${FSLDIR}/bin/bet $I ${I}_brain -s -m $betopts >> report.sienax
${FSLDIR}/bin/fslmaths ${I}_brain -sub `$FSLDIR/bin/fslstats ${I}_brain -p 0` -mas ${I}_MONSTR_brain_mask ${I}_brain -odt float


echo $I
echo ${Io}_brain
remainder="${Io}"
echo ${remainder} | awk -F/ '{print $8}'
T1=`echo ${remainder} | awk -F/ '{print $8}'`
echo $T1
echo $lt

echo $Io
#python /data/henry6/gina/scripts/grid_submit.py "/data/henry6/gina/scripts/MONSTR.py -i $Io"
python /data/henry6/gina/scripts/MONSTR.py -i $Io
echo $T1_MONSTR.nii.gz
echo $T1_MONSTR_brain.nii.gz I_brain.nii.gz

${FSLDIR}/bin/fslmaths $T1_MONSTR_brain.nii.gz $T1_MONSTR_brain.nii.gz
${FSLDIR}/bin/fslmaths $T1_MONSTR_brain_mask.nii.gz $T1_MONSTR_brain_mask.nii.gz

${FSLDIR}/bin/overlay 0 0 $I -a $T1_MONSTR_brain 1 `${FSLDIR}/bin/fslstats $T1_MONSTR_brain -P 95` $T1_MONSTR_brain_skull 0.9 1.1 $T1_grot
${FSLDIR}/bin/slicer $T1_grot -a $T1_bet.png
${FSLDIR}/bin/imrm $T1_grot
echo "<hr><p><b>BET brain extraction results</b><p><IMG BORDER=0 SRC=\"$T1_bet.png\">" >> report.html

echo ""                                                                        >> report.sienax
echo "----------  register to standard space using brain and skull  --------" >> report.sienax
echo "(do not worry about histogram warnings)"                                 >> report.sienax
${FSLDIR}/bin/pairreg ${FSLDIR}/data/standard/MNI152_T1_2mm_brain $T1_MONSTR_brain ${FSLDIR}/data/standard/MNI152_T1_2mm_skull $T1_MONSTR_brain_skull $T12std.mat -searchrx -180 180 -searchry -180 180 -searchrz -180 180 >> report.sienax 2>&1
${FSLDIR}/bin/avscale $T12std.mat ${FSLDIR}/data/standard/MNI152_T1_2mm > $T12std.avscale
xscale=`grep Scales $T12std.avscale | awk '{print $4}'`
yscale=`grep Scales $T12std.avscale | awk '{print $5}'`
zscale=`grep Scales $T12std.avscale | awk '{print $6}'`
vscale=`echo "10 k $xscale $yscale * $zscale * p"|dc -`
echo "VSCALING $vscale" >> report.sienax
${FSLDIR}/bin/flirt -in $I -ref ${FSLDIR}/data/standard/MNI152_T1_2mm_brain -o $T12std -applyxfm -init $T12std.mat
${FSLDIR}/bin/slicer $T12std ${FSLDIR}/data/standard/MNI152_T1_2mm_brain -a $T12std.png
${FSLDIR}/bin/imrm $T12std
echo "<hr><p><b>FLIRT standard space registration results</b><p><IMG BORDER=0 SRC=\"$T12std.png\">" >> report.html

echo ""                                                                        >> report.sienax
echo "----------  mask with std mask  ---------------------------------------" >> report.sienax
${FSLDIR}/bin/convert_xfm -inverse -omat $T12std_inv.mat $T12std.mat
MASK=${FSLDIR}/data/standard/MNI152_T1_2mm_brain_mask_dil
if [ "$stdroi" != "" ] ; then
    ${FSLDIR}/bin/fslmaths $MASK $stdroi $T1_stdmaskroi
    MASK=$T1_stdmaskroi
fi
${FSLDIR}/bin/flirt -in $MASK -ref $T1_MONSTR_brain -out $T1_stdmask -applyxfm -init $T12std_inv.mat
${FSLDIR}/bin/fslmaths $T1_stdmask -thr 0.5 -bin $T1_stdmask
${FSLDIR}/bin/fslmaths $T1_MONSTR_brain -mas $T1_stdmask $T1_stdmaskbrain
${FSLDIR}/bin/overlay 0 0 -c $I -a $T1_stdmask 0.9 3 $T1_MONSTR_brain_mask 0.9 1.1 $T1_grot
${FSLDIR}/bin/slicer $T1_grot -a $T1_masks.png
${FSLDIR}/bin/imrm $T1_grot
echo "<hr><p><b>Field-of-view and standard space masking</b><br>Red shows the standard-space-based brain mask combined with the field-of-view mask (if used). Blue shows the original BET-derived brain mask. Green shows the intersection of the two.<p><IMG BORDER=0 SRC=\"$T1_masks.png\">" >> report.html

if [ $regional = 1 ] ; then
    ${FSLDIR}/bin/flirt -in ${FSLDIR}/data/standard/MNI152_T1_2mm_strucseg_periph -ref $T1_MONSTR_brain -out $T1_stdmask_segperiph -applyxfm -init $T12std_inv.mat
    ${FSLDIR}/bin/fslmaths $T1_stdmask_segperiph -thr 0.5 -bin $T1_stdmask_segperiph
    ${FSLDIR}/bin/fslmaths ${FSLDIR}/data/standard/MNI152_T1_2mm_strucseg -thr 4.5 -bin $T1_tmpmask
    ${FSLDIR}/bin/flirt -in $T1_tmpmask -ref $T1_MONSTR_brain -out $T1_stdmask_segvent -applyxfm -init $T12std_inv.mat
    ${FSLDIR}/bin/fslmaths $T1_stdmask_segvent -thr 0.5 -bin $T1_stdmask_segvent
    /bin/rm $T1_tmpmask*
fi

echo ""                                                                        >> report.sienax
echo "----------  segment tissue into types  --------------------------------" >> report.sienax
if [ $nseg = 2 ] ; then
    ${FSLDIR}/bin/fast -g -n 2 $imtype $segopts $T1_stdmaskbrain >> report.sienax 2>&1
    echo "" >> report.sienax
    echo "----------  convert brain volume into normalised volume  --------------" >> report.sienax
    echo "" >> report.sienax
    echo "                   volume    unnormalised-volume" >> report.sienax
    S=`${FSLDIR}/bin/fslstats $T1_stdmaskbrain_pve_1 -m -v`
    xa=`echo $S | awk '{print $1}'`
    xb=`echo $S | awk '{print $3}'`
    ubrain=`echo "2 k $xa $xb * 1 / p" | dc -`
    nbrain=`echo "2 k $xa $xb * $vscale * 1 / p" | dc -`
else
    if [ _$lm != _ ] ; then
	${FSLDIR}/bin/fslmaths $lm -bin -mul -1 -add 1 -mul $T1_stdmaskbrain $T1_stdmaskbrain -odt float
    fi

    ${FSLDIR}/bin/fast -g $imtype $segopts $T1_stdmaskbrain >> report.sienax 2>&1

    if [ _$lm != _ ] ; then
	${FSLDIR}/bin/fslmaths $lm -bin -max $T1_stdmaskbrain_pve_2 $T1_stdmaskbrain_pve_2 -odt float
	${FSLDIR}/bin/fslmaths $lm -bin -mul 3 -max $T1_stdmaskbrain_seg $T1_stdmaskbrain_seg -odt int
    fi

    echo "" >> report.sienax
    echo "----------  convert brain volume into normalised volume  --------------" >> report.sienax
    echo "" >> report.sienax
    echo "tissue             volume    unnormalised-volume" >> report.sienax
    if [ $regional = 1 ] ; then
	${FSLDIR}/bin/fslmaths $T1_stdmaskbrain_pve_1 -mas $T1_stdmask_segperiph $T1_stdmaskbrain_pve_1_segperiph -odt float
	S=`${FSLDIR}/bin/fslstats $T1_stdmaskbrain_pve_1_segperiph -m -v`
	xa=`echo $S | awk '{print $1}'`
	xb=`echo $S | awk '{print $3}'`
	uxg=`echo "2 k $xa $xb * 1 / p" | dc -`
	xg=`echo "2 k $xa $xb * $vscale * 1 / p" | dc -`
	echo "pgrey              $xg $uxg (peripheral grey)" >> report.sienax

	${FSLDIR}/bin/fslmaths $T1_stdmaskbrain_pve_0 -mas $T1_stdmask_segvent $T1_stdmaskbrain_pve_0_segvent -odt float
	S=`${FSLDIR}/bin/fslstats $T1_stdmaskbrain_pve_0_segvent -m -v`
	xa=`echo $S | awk '{print $1}'`
	xb=`echo $S | awk '{print $3}'`
	uxg=`echo "2 k $xa $xb * 1 / p" | dc -`
	xg=`echo "2 k $xa $xb * $vscale * 1 / p" | dc -`
	echo "vcsf               $xg $uxg (ventricular CSF)" >> report.sienax
    fi
    S=`${FSLDIR}/bin/fslstats $T1_stdmaskbrain_pve_1 -m -v`
    xa=`echo $S | awk '{print $1}'`
    xb=`echo $S | awk '{print $3}'`
    ugrey=`echo "2 k $xa $xb * 1 / p" | dc -`
    ngrey=`echo "2 k $xa $xb * $vscale * 1 / p" | dc -`
    echo "GREY               $ngrey $ugrey" >> report.sienax
    S=`${FSLDIR}/bin/fslstats $T1_stdmaskbrain_pve_2 -m -v`
    xa=`echo $S | awk '{print $1}'`
    xb=`echo $S | awk '{print $3}'`
    uwhite=`echo "2 k $xa $xb * 1 / p" | dc -`
    nwhite=`echo "2 k $xa $xb * $vscale * 1 / p" | dc -`
    echo "WHITE              $nwhite $uwhite" >> report.sienax

    ubrain=`echo "2 k $uwhite $ugrey + 1 / p" | dc -`
    nbrain=`echo "2 k $nwhite $ngrey + 1 / p" | dc -`
fi

echo "BRAIN              $nbrain $ubrain" >> report.sienax

${FSLDIR}/bin/overlay 1 1 -c $T1 -a $T1_stdmaskbrain_seg 1.9 5 $T1_render
${FSLDIR}/bin/slicer $T1_render -s 1 -x 0.4 gr$T1a.png -x 0.5 gr$T1b.png -x 0.6 gr$T1c.png -y 0.4 gr$T1d.png -y 0.5 gr$T1e.png -y 0.6 gr$T1f.png -z 0.4 gr$T1g.png -z 0.5 gr$T1h.png -z 0.6 gr$T1i.png
${FSLDIR}/bin/pngappend gr$T1a.png + gr$T1b.png + gr$T1c.png + gr$T1d.png + gr$T1e.png + gr$T1f.png + gr$T1g.png + gr$T1h.png + gr$T1i.png $T1_render.png
/bin/rm gr$T1?.???

echo "<hr><p><b>Final SIENAX segmentation results</b><p>Whole-brain segmentation<br><IMG BORDER=0 SRC=\"$T1_render.png\">" >> report.html

if [ $regional = 1 ] ; then
    ${FSLDIR}/bin/overlay 0 1 -c $T1 -a $T1_stdmaskbrain_pve_1_segperiph 0.3 0.7 $T1_periph_render
    ${FSLDIR}/bin/overlay 0 1 -c $T1 -a $T1_stdmaskbrain_pve_0_segvent   0.3 0.7 $T1_vent_render
    ${FSLDIR}/bin/slicer $T1_periph_render -s 1 -x 0.4 gr$T1a.png -x 0.5 gr$T1b.png -x 0.6 gr$T1c.png -y 0.4 gr$T1d.png -y 0.5 gr$T1e.png -y 0.6 gr$T1f.png -z 0.4 gr$T1g.png -z 0.5 gr$T1h.png -z 0.6 gr$T1i.png
    ${FSLDIR}/bin/pngappend gr$T1a.png + gr$T1b.png + gr$T1c.png + gr$T1d.png + gr$T1e.png + gr$T1f.png + gr$T1g.png + gr$T1h.png + gr$T1i.png $T1_periph_render.png
    ${FSLDIR}/bin/slicer $T1_vent_render -s 1 -x 0.4 gr$T1a.png -x 0.5 gr$T1b.png -x 0.6 gr$T1c.png -y 0.4 gr$T1d.png -y 0.5 gr$T1e.png -y 0.6 gr$T1f.png -z 0.4 gr$T1g.png -z 0.5 gr$T1h.png -z 0.6 gr$T1i.png
    ${FSLDIR}/bin/pngappend gr$T1a.png + gr$T1b.png + gr$T1c.png + gr$T1d.png + gr$T1e.png + gr$T1f.png + gr$T1g.png + gr$T1h.png + gr$T1i.png $T1_vent_render.png
    /bin/rm gr$T1?.???
    echo "<p>Peripheral cortex masked segmentation<br><IMG BORDER=0 SRC=\"$T1_periph_render.png\"><p>Ventricle masked segmentation<br><IMG BORDER=0 SRC=\"$T1_vent_render.png\">" >> report.html
fi

if [ $debug = 0 ] ; then
    /bin/rm -f `$FSLDIR/bin/imglob -extensions $T1_MONSTR_brain* $T1_stdmask*`
    /bin/rm -f $T12std.avscale $T12std_inv.mat
fi

echo "<p>Estimated volumes:<br><pre>" >> report.html
${FSLDIR}/bin/extracttxt unnormalised report.sienax >> report.html
echo "</pre>" >> report.html

echo ""
echo "Finished. The SIENAX report can be viewed by pointing your web browser at:"
echo file:`pwd`/report.html
echo "Estimated normalised brain volume (NBV) ="
echo "$nbrain"
echo ""

cat >> report.html <<EOF

<hr><p><b>SIENAX Methods</b>

<p>Brain tissue volume, normalised for subject head size, was
estimated with SIENAX [Smith 2001, Smith 2002], part of FSL [Smith
2004]. SIENAX starts by extracting brain and skull images from the
single whole-head input data [Smith 2002b]. The brain image is then
affine-registered to MNI152 space [Jenkinson 2001, Jenkinson 2002]
(using the skull image to determine the registration scaling); this is
primarily in order to obtain the volumetric scaling factor, to be used
as a normalisation for head size. Next, tissue-type segmentation with
partial volume estimation is carried out [Zhang 2001] in order to
calculate total volume of brain tissue (including separate estimates
of volumes of grey matter, white matter, peripheral grey matter and
ventricular CSF).

<font size=-1><em>
<P>[Smith 2001] S.M. Smith, N.&nbsp;De&nbsp;Stefano, M.&nbsp;Jenkinson, and P.M. Matthews.
<BR>&nbsp;&nbsp;&nbsp;Normalised accurate measurement of longitudinal brain change.
<BR>&nbsp;&nbsp;&nbsp;Journal of Computer Assisted Tomography, 25(3):466-475, May/June 2001.

<P>[Smith 2002] S.M. Smith, Y.&nbsp;Zhang, M.&nbsp;Jenkinson, J.&nbsp;Chen, P.M. Matthews, A.&nbsp;Federico, and N.&nbsp;De&nbsp;Stefano.
<BR>&nbsp;&nbsp;&nbsp;Accurate, robust and automated longitudinal and cross-sectional brain change analysis.
<BR>&nbsp;&nbsp;&nbsp;NeuroImage, 17(1):479-489, 2002.

<P>[Smith 2004] S.M. Smith, M.&nbsp;Jenkinson, M.W. Woolrich, C.F. Beckmann, T.E.J. Behrens, H.&nbsp;Johansen-Berg, P.R. Bannister, M.&nbsp;De&nbsp;Luca, I.&nbsp;Drobnjak, D.E. Flitney, R.&nbsp;Niazy, J.&nbsp;Saunders, J.&nbsp;Vickers, Y.&nbsp;Zhang, N.&nbsp;De&nbsp;Stefano, J.M. Brady, and P.M. Matthews.
<BR>&nbsp;&nbsp;&nbsp;Advances in functional and structural MR image analysis and
  implementation as FSL.
<BR>&nbsp;&nbsp;&nbsp;NeuroImage, 23(S1):208-219, 2004.

<P>[Smith 2002b] S.M. Smith.
<BR>&nbsp;&nbsp;&nbsp;Fast robust automated brain extraction.
<BR>&nbsp;&nbsp;&nbsp;Human Brain Mapping, 17(3):143-155, November 2002.

<P>[Jenkinson 2001] M.&nbsp;Jenkinson and S.M. Smith.
<BR>&nbsp;&nbsp;&nbsp;A global optimisation method for robust affine registration of brain images.
<BR>&nbsp;&nbsp;&nbsp;Medical Image Analysis, 5(2):143-156, June 2001.

<P>[Jenkinson 2002] M.&nbsp;Jenkinson, P.R. Bannister, J.M. Brady, and S.M. Smith.
<BR>&nbsp;&nbsp;&nbsp;Improved optimisation for the robust and accurate linear registration and motion correction of brain images.
<BR>&nbsp;&nbsp;&nbsp;NeuroImage, 17(2):825-841, 2002.

<P>[Zhang 2001] Y.&nbsp;Zhang, M.&nbsp;Brady, and S.&nbsp;Smith.
<BR>&nbsp;&nbsp;&nbsp;Segmentation of brain MR images through a hidden Markov random field model and the expectation maximization algorithm.
<BR>&nbsp;&nbsp;&nbsp;IEEE Trans. on Medical Imaging, 20(1):45-57, 2001.

EOF

