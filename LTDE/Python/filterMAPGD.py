from __future__ import division
import pandas as pd
import os, math
import numpy as np
import scipy.stats as st
import csv
import annotateFuncs as af
mydir = os.path.expanduser("~/github/Task2/LTDE")

strain_dict = {'ATCC13985': 'Pseudomonas', 'ATCC43928': 'Pseudomonas', \
'KBS0702': 'Arthrobacter', 'KBS0703': 'Arthrobacter', 'KBS0705':'Inquilinus', \
'KBS0706':'Mycobacterium', 'KBS0707': 'Pseudomonas', 'KBS0710': 'Pseudomonas', \
'KBS0711': 'Janthinobacterium', 'KBS0712': 'Variovorax', 'KBS0713': 'Yersinia', \
'KBS0715': 'Curtobacterium', 'KBS0721': 'Flavobacterium', 'KBS0722': 'Oerskovia', \
'KBS0724': 'Rhodococcus', 'KBS0727': 'Bradyrhizobium', 'KBS0801': 'Burkholderia', \
'KBS0802': 'Pseudomonas', 'KBS0812': 'Bacillus'}

class popGenStats:
    '''
    A class to estimate Tajima's D using pi (Tajima's theta), S,
    and N (in this case mean coverage)
    '''

    def __init__(self, pi, S, n):
        self.pi = float(pi)
        self.S = int(S)
        self.n = int(n)

    def a1(self):
        '''Given n, this function returns the (n-1)th harmonic number'''
        return sum((1.0/d) for d in range(1,self.n))

    def a2(self):
        '''Given n, this function returns the (n-1)th squared harmonic number'''
        return sum((1.0/(d**2)) for d in range(1,self.n))

    def b1(self):
        '''Creates b1 for the variance of Tajima's theta'''
        return ((self.n+1) /  (3*(self.n-1)))

    def b2(self):
        '''Creates b2 for the variance of Tajima's theta'''
        num = ((self.n**2) + self.n + 3) * 2
        den = 9 * self.n * (self.n-1)
        return num / den

    def c1(self):
        '''Creates c1 for the variance of Tajima's theta'''
        return self.b1() - (1 / self.a1())

    def c2(self):
        '''Creates c2 for the variance of Tajima's theta'''
        return self.b2() - ((self.n+2) / (self.a1() * self.n)) + (self.a2() / (self.a1() ** 2 ))

    def e1(self):
        return self.c1() / self.a1()

    def e2(self):
        return self.c2() / ( (self.a1() ** 2) + self.a2() )

    def W_theta(self):
        if self.S == 0:
            theta = int(0)
        else:
            theta = self.S / self.a1()
        return theta

    def W_theta_variance(self):
        term1 = self.W_theta() / self.a1()
        term2 = (self.a2() / ( self.a1() ** 2))  * (self.W_theta() ** 2 )
        return term1 + term2

    def tajimas_D(self):
        Wattersons = self.W_theta()
        num = self.pi - Wattersons
        den = math.sqrt( (self.e1() * self.S) + (self.e2() * self.S * (self.S-1)) )
        T_D = num / den
        return T_D


def pandasNames(df):
    names = ['Scaffold', 'Pos', 'Major', 'Minor', 'Coverage', 'Error', \
        'Gene', 'AA-change', 'Fourfold']
    samples = len(df.columns) - len(names)
    for x in range(samples):
        name = 'Sample_' + str(x+1)
        names.append(name)
    df.columns = names
    df.iloc[:,8:] = df.iloc[:,8:].convert_objects(convert_numeric=True)
    return (df, samples)

def getPiVar(pi, n):
    '''
    returns the variance for pi
    got here: http://genapps.uchicago.edu/slider/index.html
    Also in Walsh & Lynch 201?
    '''
    if pi == 0:
        return 0
    else:
        x1 = ((n+1) / (3* (n-1))) * pi
        x2 = ((( (n**2) + n +3 ) * 2 ) / (9*n * (n-1)) ) * (pi**2)
        return x1 + x2


def getPolyTable(taxa):
    polyDict = {}
    for taxon in taxa:
        IN = pd.read_csv(mydir + '/data/mapgd/annotate/' + taxon + '_merged_annotate.txt', delimiter = '\t', \
            header = None)
        names_IN = pandasNames(IN)
        IN = names_IN[0]
        IN_samples = names_IN[1]
        # count polymorphisms in coding vs noncoding

        # non coding and coding subsets
        NC_count = IN[IN.apply(lambda x: (x.iloc[6] == 'NC'), axis=1 )]
        C_count = IN[IN.apply(lambda x: (x.iloc[6] != 'NC'), axis=1 )]
        C_S_count = IN[IN.apply(lambda x:  (x.iloc[7] == 'S'), axis=1 )]
        samples_NC = []
        samples_C = []
        for x in range(1, IN_samples):
            sample_column = 'Sample_' + str(x)
            NC_x =  sum(sum([(NC_count[sample_column] > (float(0))) & (NC_count[sample_column]< (float(1)))]))
            #NC_x = (NC_count[sample_column]  > (float(0))) and  (NC_count[sample_column]  < (float(1)))
            C_x =  sum(sum([(C_count[sample_column] > (float(0))) & (C_count[sample_column]< (float(1)))]))
            #C_x = (C_count[sample_column]  != (float(0)  or float(1))).count()
            samples_NC.append(NC_x)
            samples_C.append(C_x)
        NC_mean = np.mean(samples_NC)
        NC_std = np.std(samples_NC)
        C_mean = np.mean(samples_C)
        C_std = np.std(samples_C)
        polyDict[taxon] = [NC_mean, NC_std, C_mean, C_std]
        #ones_and_zeroes = IN[IN.apply(lambda x: ((x.iloc[8:]==float(1)).sum() !=0 \
        #        or (x.iloc[8:]==float(0)).sum() !=0) and  x.iloc[6] != 'NC', axis=1) ]
        #ones_and_zeroes_path = mydir + '/data/mapgd/final/coding/' + taxon + '_coding.txt'
        #ones_and_zeroes.to_csv(ones_and_zeroes_path,sep='\t')
    df = pd.DataFrame(polyDict)
    df = df.transpose()
    df.columns = ['NC_mean', 'NC_std', 'C_mean', 'C_std']
    latex_path = mydir + '/tables/test.tex'
    df.to_latex(latex_path)

def getPotentialMutations(taxa):
    for taxon in taxa:
        IN = pd.read_csv(mydir + '/data/mapgd/annotate/' + taxon + '_merged_annotate.txt', delimiter = '\t', \
            header = None)
        names_IN = pandasNames(IN)
        IN = names_IN[0]
        IN_samples = names_IN[1]
        for index, row in IN.iterrows():
            print row[9:].values


def getNumberSilentSitesAll(strain):
    if strain == 'KBS0812':
        GFF = mydir + '/data/Bacillus_test/AL009126.3.gff'
        FFN = mydir + '/data/Bacillus_test/AL009126.fa'
    elif strain in af.KBSGenomes():
        GFF = mydir + '/data/2016_KBSGenomes_Annotate/' + strain + '/G-Chr1.gff'
        FFN = mydir + '/data/2016_KBSGenomes_Annotate/' + strain + '/G-Chr1.fna'
    else:
        GFF = mydir + '/data/2015_SoilGenomes_Annotate/' + strain + '/G-Chr1.gff'
        FFN = mydir + '/data/2015_SoilGenomes_Annotate/' + strain + '/G-Chr1.fna'
    return af.annotate(GFF, FFN).countFourfoldSites()


def getPi(strains, folded = True):
    piDict = {}
    OUT = open(mydir + '/data/mapgd/final/PopGenStats.txt', 'w')
    print>> OUT, 'Strain', 'Genus', 'Replicate', 'Pi', 'Pi_var', 'Pi_prob', 'W_theta', 'W_theta_var', 'T_D'
    for strain in strains:
        fourfoldCount = getNumberSilentSitesAll(strain)
        genus = strain_dict[strain]
        IN = pd.read_csv(mydir + '/data/mapgd/annotate/' + strain + '_merged_annotate.txt', delimiter = '\t', \
            header = None)

        names_IN = pandasNames(IN)
        IN = names_IN[0]
        IN_samples = names_IN[1]
        C_S_count = IN[IN.apply(lambda x:  (x.iloc[7] == 'S') and(x.iloc[8] == 'Y'), axis=1 )]
        pi = []
        piVar = []
        W_theta = []
        T_D = []
        W_theta_var = []
        for x in range(1, IN_samples + 1):
            if strain == 'KBS0711':
                if x == 1:
                    rep = 'L'
                elif x == 2:
                    rep = 'A'
                elif x == 3:
                    rep = 'C'
                elif x == 4:
                    rep = 'D'
                elif x == 5:
                    rep = 'K'
                elif x == 6:
                    rep = 'WA'
                elif x == 7:
                    rep = 'WB'
                elif x == 8:
                    rep = 'WC'
                elif x == 9:
                    rep = 'WD'
            elif strain == 'ATCC43928':
                if x == 1:
                    rep = 'A'
                elif x == 2:
                    rep = 'B'
                elif x == 3:
                    rep = 'C'
                elif x == 4:
                    continue
                elif x == 5:
                    rep = 'D'
            else:
                if x == 1:
                    rep = 'A'
                elif x == 2:
                    rep = 'B'
                elif x == 3:
                    rep = 'C'
                elif x == 4:
                    rep = 'D'


            sample_column = 'Sample_' + str(x)
            pi_subset_names = ['Coverage', sample_column]
            pi_subset = C_S_count[pi_subset_names]

            pi_subset_tuples = [tuple(y) for y in pi_subset.values]
            pi_x = []
            N_x = []
            S = 0
            for value in pi_subset_tuples:
                if folded == True and value[1] == float(1.0):
                    continue
                S += 1
                p = value[1]
                q = 1- p
                N = value[0]
                pi_value = (N / (N-1) ) * p * q * 2
                pi_x.append(pi_value)
                N_x.append(N)
            # sum over pi
            pi_x_sum = sum(pi_x)
            if pi_x_sum == float(0) and S == int(0):
                T_D.append(0)
                pi.append(0)
                piVar.append(0)
                W_theta.append(0)
            # calculate mean N for the variance of pi
            else:
                N_x_mean = np.mean(N_x)
                W_theta_x = popGenStats(pi_x_sum, S, N_x_mean).W_theta()
                W_theta_var_x = popGenStats(pi_x_sum, S, N_x_mean).W_theta_variance()
                T_D_x = popGenStats(pi_x_sum, S, N_x_mean).tajimas_D()
                pi_x_var = getPiVar(pi_x_sum, N_x_mean)
                T_D.append(T_D_x)
                pi.append(pi_x_sum)
                piVar.append(pi_x_var)
                W_theta.append(W_theta_x)
                W_theta_var.append(W_theta_var_x)
                print>> OUT, strain, genus, rep, pi_x_sum, \
                    pi_x_var, pi_x_sum/fourfoldCount , W_theta_x, W_theta_var_x, T_D_x
        pi_mean = np.mean(pi)
        pi_var = np.mean(piVar)
        W_theta_mean = np.mean(W_theta)
        T_D_mean = np.mean(T_D)
        T_D_SD = np.std(T_D)
        print pi_mean /fourfoldCount
        piDict[strain] = [genus, pi_mean, pi_var, pi_mean /fourfoldCount ,W_theta_mean, T_D_mean, T_D_SD]
    OUT.close()
    df = pd.DataFrame(piDict, index=None)
    df = df.transpose()
    df.reset_index(level=0, inplace=True)
    df.columns = ['Strain', 'Genus', 'Pi_mean', 'Pi_var', 'Pi_prob', 'W_theta_mean', 'T_D_mean', 'T_D_SD']
    df_path = mydir + '/data/mapgd/final/PopGenStatsSummary.txt'
    df.to_csv(df_path,sep='\t')





taxa = ['ATCC13985', 'ATCC43928', 'KBS0702', 'KBS0703', \
    'KBS0707', 'KBS0710', 'KBS0711','KBS0712', 'KBS0713', \
    'KBS0715', 'KBS0721', 'KBS0722', 'KBS0724', 'KBS0727', 'KBS0801', \
    'KBS0802', 'KBS0812']
#getPolyTable(taxa)
#getPi(taxa)
getPotentialMutations(taxa)
