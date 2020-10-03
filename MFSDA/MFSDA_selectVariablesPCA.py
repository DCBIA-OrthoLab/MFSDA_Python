from __future__ import print_function
from sklearn.decomposition import PCA
import pandas as pd
import sklearn.preprocessing 
import scipy.stats
import csv
import sys
import numpy as np
import argparse
import json
import os
import os.path as path
import matplotlib.pyplot as plt
import matplotlib
# import matplotlib.pyplot
# matplotlib.use('pyplot')
from matplotlib.backends.backend_pdf import PdfPages
import datetime
# plt.plot([1,2,3,4])
# plt.ylabel('some numbers')
# plt.show()

# pearson correlation
def main():
    parser = argparse.ArgumentParser(description='Variable selection using Correlation with Principal Components.')
    parser.add_argument('--csv', type=str, help='all the covariates for each patient', required=True)
    parser.add_argument('--output', help='output directory to write output', default='./' , type=str)
    parser.add_argument('--num_components', help='number of components to keep in PCA', default=2)
    args = parser.parse_args()
    run_pc_score(args)
    print('Done!')
# group    patientId    aNGSA    aNGP    bDNFSA    bDNFP    mMP3SA    mMP3P    mMP7SA    mMP7P    pAIISA    pAIIP    tIMP1SA    tIMP1P    vECadherinSA    vECadherinP    ckineSA    ckineP    cXCL16SA    cXCL16P    eNA78SA    eNA78P    gMCSFSA    gMCSFP    iFNgSA    iFNgP    iL1aSA    iL1aP    iL6SA    iL6P    tGFB1SA    tGFB1P    tNFaSA    tNFaP    vEGFSA    vEGFP
# patientId,aNGSA,aNGP,bDNFSA,bDNFP,mMP3SA,mMP3P,mMP7SA,mMP7P,pAIISA,pAIIP,tIMP1SA,tIMP1P,vECadherinSA,vECadherinP,ckineSA,ckineP,cXCL16SA,cXCL16P,eNA78SA,eNA78P,gMCSFSA,gMCSFP,iFNgSA,iFNgP,iL1aSA,iL1aP,iL6SA,iL6P,tGFB1SA,tGFB1P,tNFaSA,tNFaP,vEGFSA,vEGFP,owner,formId,date,type,$$hashKey
# usecols=['aNGSA', 'mMP3SA' ,'mMP7SA', 'tIMP1SA', 'vECadherinSA','cXCL16SA' ,'eNA78SA', 'vEGFSA']

def run_pc_score(args):
    covariates_sa = pd.read_csv(args.csv)
    covariates = np.array(covariates_sa.axes[1])
    if type(covariates[0]) == str:
        covariates_sa = pd.read_csv(args.csv, usecols=covariates)
    else:
        covariates_sa = np.array(covariates_sa)  # à suppr pour bio !!!
        covariates_sa_size = np.shape(covariates_sa)
        covariates_group=[]
    covariates_sa = np.array(covariates_sa)
    covariates_group=covariates_sa
    covariates_group_size = np.shape(covariates_group)
    print(covariates_group_size)
    for i in range(0, covariates_group_size[0]):
        for j in range(0, covariates_group_size[1]):
            if covariates_group[i][j]=='yes':
                covariates_group[i][j]=1
            if covariates_group[i][j]=='no':
                covariates_group[i][j]=0
            covariates_group[i][j] = float(covariates_group[i][j])
    covariates_group = np.array(covariates_group)
    num_components=int(args.num_components);
    X_ = np.mean(covariates_group, axis=0)
    normalized=sklearn.preprocessing.normalize(covariates_group)
    covariates_group_n=normalized.transpose()
    pear=[]
    pval=[]
    pval_withoutcov=[]
    [Dir, ext]=path.splitext(args.output)
    if not path.exists(args.output):
        diroutput = args.output
        os.makedirs(diroutput)
    else: 
        diroutput = args.output
    pathPdf=path.join(diroutput, 'Plot_covariates_for_each_patient.pdf')
    pdf=PdfPages(pathPdf)
    plt.figure(figsize=(13,7.5))
    plt.title('Linear representation of the covariates')
    for num_c in range(0,covariates_group_size[1]):
        plt.plot(covariates_group_n[num_c], label=covariates[num_c])
        pear.append([])
        pval.append([])
        pval_withoutcov.append([])
        for num in range(0,covariates_group_size[1]):
            [pe,pv]=scipy.stats.pearsonr(covariates_group[:,num_c],covariates_group[:,num])
            pear[num_c].append(pe)
            pval[num_c].append(pv)
            pval_withoutcov[num_c].append(pv)
    plt.legend(bbox_to_anchor=(0., 1., 1., 0.), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)
    plt.xlabel('patientId')
    pdf.savefig()
    # plt.show()
    
    pear=np.array(pear).tolist()
    pval_withoutcov=np.array(pval_withoutcov).tolist()
    plt.figure(figsize=(13,7.5))
    plt.title('Pearson Correlation')
    c = plt.pcolor(pear, edgecolors='k', linewidths=4, cmap='RdBu', vmin=0.0, vmax=1.0)
    c.update_scalarmappable()
    ax = c.axes
    fmt="%.3f"
    for p, color, value in zip(c.get_paths(), c.get_facecolors(), c.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        ax.text(x, y, fmt % value, ha="center", va="center", color=color)
    plt.colorbar(c)
    plt.gca().invert_yaxis()
    posx = []
    posy=[]
    xc = 0.5
    yc = 0.5
    for c in covariates:
        posx.append(xc)
        posy.append(yc)
        xc += 1
        yc += 1
    plt.xticks(posx, covariates, rotation=45)
    plt.yticks(posy, covariates)
    pdf.savefig()
    # plt.show()
    plt.figure(figsize=(13,7.5))
    plt.title('p-values')
    bounds = [0.0, 0.01, 0.05, 0.050000001, 1]
    cmap=matplotlib.colors.ListedColormap(['r', (1.0, 1.0, 0.0), 'g', 'b'])
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    c = plt.pcolor(pval, edgecolors='k', linewidths=4, cmap=cmap, norm=norm)
    c.update_scalarmappable()
    ax = c.axes
    fmt="%.3f"
    for p, color, value in zip(c.get_paths(), c.get_facecolors(), c.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        if value >= 0.01 and value < 0.05:
            color= (0.0, 0.0, 0.0)
        ax.text(x, y, fmt % value, ha="center", va="center", color=color)
    plt.colorbar(c)
    plt.gca().invert_yaxis()
    plt.xticks(posx, covariates, rotation=45)
    plt.yticks(posy, covariates)
    pdf.savefig()
    # plt.show()
    pdf.close()



    pca = PCA(n_components=num_components)  # nombre d'axe qu'on veut !
    

    test=sklearn.preprocessing.normalize(covariates_group - X_)
    X_pca = pca.fit_transform(covariates_group)  # X toutes les covariates et X_ mean !
    percentage_ratio = pca.explained_variance_ratio_
    print('ratio', pca.explained_variance_ratio_)

    
    pearsoncorr=[]
    pearson=[]
    for num_c in range(num_components):
        pearsoncorr.append([])
        for i in range(covariates_group_size[1]):
            pearsoncorr[num_c].append(scipy.stats.pearsonr(X_pca[:,num_c],covariates_group[:,i]))
            [pearson_coef,pvalues]=scipy.stats.pearsonr(X_pca[:,num_c],covariates_group[:,i])

    pearsoncorr = np.array(pearsoncorr)
    print("pearsoncorr", pearsoncorr)
    outcorrpca = {}
    outcorrpca["covariates"] = covariates.tolist()
    outcorrpca["pca"] = X_pca.tolist()
    outcorrpca["pearsoncorr"] = pearsoncorr.tolist()
    outcovariates = {}
    outcovariates["covariates"] = covariates.tolist()

    shapepears = np.shape(pearsoncorr)

    csvout = ','
    csvout2 = ','
    
    for i in range(shapepears[1]):
        pear[i].insert(0,covariates[i])
        pval[i].insert(0,covariates[i])
        csvout2 += covariates[i]
        csvout += covariates[i]
        csvout2 += ','
        csvout += ','
    csvout += '\n'
    csvout2 += '\n'
    for i in range(shapepears[0]):
        csvout+= 'PC_Score'+str(i+1)
        csvout2+= 'PC_Score'+str(i+1)
        csvout2 += ','
        csvout += ','
        for j in range(shapepears[1]):
            [pca, pvalue]=pearsoncorr[i][j]
            csvout += str(pca) # add the pearson coeff
            csvout2 += str(pvalue) # add p-value
            csvout += ','
            csvout2 += ','
        csvout += '\n'
        csvout2 += '\n'
    csvout=csvout.split('\n')
    csvout2=csvout2.split('\n')
    print("valuesF",pval)
    for i in range(0,shapepears[0]+1):
        csvout[i]=csvout[i].split(',')
        csvout2[i]=csvout2[i].split(',')
    pathcsv=path.join(diroutput, 'pearsoncorr.csv')
    pathcsvFirst=path.join(diroutput, 'pearsonFirst.csv')
    pathcsvFirst_Pval=path.join(diroutput, 'pvaluesFirst.csv')
    percentage_num_component = path.join(diroutput, 'percentage.csv')
    outcovariates["pearsoncorr"] = pval_withoutcov
    with open(percentage_num_component, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(percentage_ratio)
    with open(pathcsv, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(0,num_components+1):
            writer.writerow(csvout[i])
        writer.writerow(' ')
        writer.writerow(' ')
        writer.writerow(' ')
        for i in range(0,num_components+1):
            writer.writerow(csvout2[i])
    with open(pathcsvFirst, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csvout[0])
        for i in range(0,covariates_group_size[1]):
            writer.writerow(pear[i])
    with open(pathcsvFirst_Pval, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csvout[0])
        for i in range(0,covariates_group_size[1]):
            writer.writerow(pval[i])
    # print("outcorrpca", outcorrpca)
    with open(path.join(diroutput, "pearsoncorr.json"), "w") as outfile:
        json.dump(outcorrpca, outfile)
    with open(path.join(diroutput, "pvaluesFirst.json"), "w") as outfile:
        json.dump(outcovariates, outfile)
    # with open(path.join(diroutput, "pvaluesFirst.json"), "w") as outfile:
    #     json.dump(outcorrpca, outfile)
    
if __name__ == '__main__':
    
    main()


