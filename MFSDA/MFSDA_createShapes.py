#!/usr/bin/env python-real
# -*- coding: utf-8 -*-
import vtk
import argparse
import os,sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.join('Resources','Libraries')))
import json
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Multivariate Functional Shape Data Analysis (MFSDA) include pvalue maps')
    parser.add_argument('--shape', type=str, help='Shape data', required=True)
    parser.add_argument('--pvalues', type=str, help='filename, .json with pvalues', required=True)
    parser.add_argument('--efit', type=str, help='filename, .json with efit', required=True)
    parser.add_argument('--covariates', nargs='+', type=str, help='vector of covariate names, ex. age gender group veCadherinP', default=None)
    parser.add_argument('--output', help='output shape', default='out.vtk')

    args = parser.parse_args()
    run_script(args)
    print('Done!')


def run_script(args):

    with open(args.pvalues) as data_file:
        pvalues = json.load(data_file)
        lpvalues = np.array(pvalues['Lpvals_fdr'])

    with open(args.efit) as data_file:
        efit = json.load(data_file)
        efitbetas = np.array(efit['efitBetas'])

    covariates = None
    if 'covariates' in pvalues and args.covariates is None:
        covariates = pvalues['covariates']
    elif args.covariates:
        covariates = args.covariates

    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(args.shape)
    reader.Update()
    shapedata = reader.GetOutput()

    pointdata = shapedata.GetPointData()    

    print("Adding pvalues...", lpvalues.shape)

    for j in range(lpvalues.shape[1]):

        arr = vtk.vtkDoubleArray()
        name = 'pvalue_'
        if covariates is not None and j < len(covariates):
            name += covariates[j]
        else:
            name += str(j)

        arr.SetName(name)

        for i in range(lpvalues.shape[0]):            
            arr.InsertNextTuple([lpvalues[i][j]])
        pointdata.AddArray(arr)

    print("Adding betas...", efitbetas.shape)

    for k in range(efitbetas.shape[2]):
        for i in range(efitbetas.shape[0]):        
            arr = vtk.vtkDoubleArray()

            name = 'betavalues_' + str(k) + "_"

            if covariates is not None and i < len(covariates):
                name += covariates[i]
            else:
                name += str(i)

            arr.SetName(name)
            
            for j in range(efitbetas.shape[1]):                
                arr.InsertNextTuple([efitbetas[i][j][k]])
            pointdata.AddArray(arr)

    print("Writing output vtk file...")

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(args.output)
    writer.SetInputData(shapedata)
    writer.Update()


if __name__ == '__main__':
    main()
