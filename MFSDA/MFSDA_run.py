#!/usr/bin/env python-real
# -*- coding: utf-8 -*-
"""
Run script: multivariate functional shape data analysis (MFSDA).

Author: Chao Huang (chaohuang.stat@gmail.com)
Last update: 2017-08-14
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.join('Resources','Libraries')))
import numpy as np
from scipy import stats
from statsmodels.sandbox.stats.multicomp import fdrcorrection0
from stat_read_x import read_x
from stat_lpks import lpks
from stat_sif import sif
from stat_wald_ht import wald_ht
from stat_bstrp_pvalue import bstrp_pvalue

import MFSDA_stat as mfsda
import timeit
import vtk
import argparse
import os
import json
import pandas as pd

"""installed all the libraries above"""

def main():
    parser = argparse.ArgumentParser(description='Multivariate Functional Shape Data Analysis (MFSDA)')
    parser.add_argument('--shapeData', type=str, help='Text file list with vtk filenames, 1 file per line', required=True)
    parser.add_argument('--covariates', type=str, nargs='+', help='name of covariates. If not specified, the csv must not have a header', default=None)
    parser.add_argument('--coordData', type=str, help='filename, .vtk shape template', required=True)
    parser.add_argument('--outputDir', help='output directory', default='./output')
    parser.add_argument('--appendCSVDir', type=str, help='Append the CSV directory to read the shape data', default=False)

    args = parser.parse_args()

    start_all = timeit.default_timer()
    run_script(args)
    stop_all = timeit.default_timer()
    delta_time_all = str(stop_all - start_all)
    print("The total elapsed time is " + delta_time_all)

def run_script(args):
    """
    Run the commandline script for MFSDA.
    """
    """+++++++++++++++++++++++++++++++++++"""
    """Step 1. load dataset """

    print("loading data ......")
    print("+++++++Read the surface shape data+++++++")

    if args.covariates:

        df = pd.read_csv(args.shapeData)
        

        y_design = []
        nshape = 0
        numpoints = -1

        for ids, row in df.iterrows():
            vtkfilename = row['file']
            if(args.appendCSVDir):
                vtkfilename = os.path.join(os.path.dirname(args.shapeData), vtkfilename)

            print("Reading {}".format(vtkfilename))
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName(vtkfilename)
            reader.Update()

            shapedata = reader.GetOutput()
            shapedatapoints = shapedata.GetPoints()

            y_design.append([])

            if numpoints == -1:
                numpoints = shapedatapoints.GetNumberOfPoints()

            if numpoints != shapedatapoints.GetNumberOfPoints():
                print("WARNING! The number of points is not the same for the shape:", vtkfilename)

            for i in range(shapedatapoints.GetNumberOfPoints()):
                p = shapedatapoints.GetPoint(i)
                y_design[nshape].append(p)

            nshape += 1

            # Build covariate matrix
            if args.covariates == ["all"]:
                for cov in df.columns:
                    if cov != "patientId" or cov != "file":
                        covs_tmp.append(row[cov])

            for cov in args.covariates:
                if cov in df.columns:
                    covs_tmp.append(row[cov])
                else:
                    print("ERROR! The name", cov, "is not a covariate in the CSV", file=sys.stderr)

    else:
        fh = open(args.shapeData, 'rU')     

        y_design = []
        nshape = 0
        numpoints = -1

        header = fh.readline()
        toks = header.split(sep=',')
        covs_tmp = []

        for line in fh.readlines():
            toks = line.strip().split(sep=',')

            # Read VTK file
            vtkfilename = toks[0].rstrip()
            print("Reading {}".format(vtkfilename))
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName(vtkfilename)
            reader.Update()
            shapedata = reader.GetOutput()
            shapedatapoints = shapedata.GetPoints()

            y_design.append([])

            if numpoints == -1:
                numpoints = shapedatapoints.GetNumberOfPoints()

            if numpoints != shapedatapoints.GetNumberOfPoints():
                print("WARNING! The number of points is not the same for the shape:", vtkfilename)

            for i in range(shapedatapoints.GetNumberOfPoints()):
                p = shapedatapoints.GetPoint(i)
                y_design[nshape].append(p)

            nshape += 1

            # Build covariate matrix
            covs_tmp.append(toks[1:])

    y_design = np.array(y_design)
    y_design.reshape(nshape, numpoints, 3)

    y_design = np.array(y_design)
    y_design.reshape(nshape, numpoints, 3) 
    print("The dimension of shape matrix is " + str(y_design.shape))

    print("+++++++Read the sphere coordinate data+++++++")
    print("Reading", args.coordData)    
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(args.coordData)
    reader.Update()
    coordData = reader.GetOutput()
    shapedatapoints = coordData.GetPoints()

    if numpoints != shapedatapoints.GetNumberOfPoints():
        print("WARNING! The template does not have the same number of points as the shapes")

    coord_mat = []
    for i in range(shapedatapoints.GetNumberOfPoints()):
        p = shapedatapoints.GetPoint(i)
        coord_mat.append(p)

    coord_mat = np.array(coord_mat)        

    # Set up design matrix
    design_data = np.array(covs_tmp,dtype=float)

    # read the covariate type
    var_type = getCovariateType(design_data)

    """+++++++++++++++++++++++++++++++++++"""
    """Step 2. Statistical analysis: including (1) smoothing and (2) hypothesis testing"""

    gpvals, lpvals_fdr, clu_pvals, efit_beta, efity_design, efit_eta = mfsda.run_stats(y_design, coord_mat, design_data, var_type)

    """+++++++++++++++++++++++++++++++++++"""
    """Step3. Save all the results"""

    if not os.path.exists(args.outputDir):
        os.makedirs(args.outputDir)

    pvalues = {}
    pvalues['Gpvals'] = gpvals.tolist()
    pvalues['clu_pvals'] = clu_pvals.tolist()
    pvalues['Lpvals_fdr'] = lpvals_fdr.tolist()

    with open(os.path.join(args.outputDir,'pvalues.json'), 'w') as outfile:
        json.dump(pvalues, outfile)

    efit = {}
    efit['efitBetas'] = efit_beta.tolist()
    efit['efitYdesign'] = efity_design.tolist()
    efit['efitEtas'] = efit_eta.tolist()

    with open(os.path.join(args.outputDir,'efit.json'), 'w') as outfile:
        json.dump(efit, outfile)


def getCovariateType(design_data):

    (row,column)=design_data.shape
    cov_types=[]
    for c in range(column):
        cov_col=design_data[:,c]
        cov_type = 0. #int
        for i in range(len(cov_col)):
            if int(cov_col[i])!=cov_col[i]:
                cov_type = 1. #double
                break
        cov_types.append(cov_type)

    cov_types = np.array(cov_types)
    return cov_types


if __name__ == '__main__':
    main()
