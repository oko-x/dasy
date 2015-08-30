'''
Created on 8.4.2015

@author: Ondrej
'''

import numpy as np
import warnings
import math

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

def calculatePercentageFromVector(vector):
    result = vector.split(';')
    count = 0
    for i, value in enumerate(result):
        result[i] = float(value)
        result[i] = round(result[i]*100,0)
        count += result[i]
    count -= 100
    result[0] -= count
    return result

def calcWeightVector(matrix):
    eigenvalues, eigenvector=np.linalg.eig(matrix)
    warnings.simplefilter("ignore", np.ComplexWarning)
    maxindex=np.argmax(eigenvalues)
    eigenvalues=np.float32(eigenvalues)
    eigenvector=np.float32(eigenvector)
    weight=eigenvector[:, maxindex] #extract vector from eigenvector with max vaue in eigenvalues
    weight.tolist() #convert array(numpy)  to vector
    weight=[ w/sum(weight) for w in weight ]
    return weight

def calcWeightMatrix(leftArray, topArray, votes, parentCrit = None):
    weightMatrix = np.eye(len(leftArray), len(topArray))
    for i, left in enumerate(leftArray):
        for j, right in enumerate(topArray):
            if weightMatrix[i,j] == 0:
                qs = votes.filter(critVarLeft=left, critVarRight=right, parentCrit=parentCrit)
                
#                 weighted geometric mean
                value = 1
                weights = 0
                for vote in qs:
                    value *= vote.value**(vote.userWeight/10)
                    weights += (vote.userWeight/10)
                if len(qs) > 0:
                    value = value**(1/weights)
                    weightMatrix[i,j] = value;
                    weightMatrix[j,i] = 1/value;     
                    
#                 weighted median
#                 valueArray = []
#                 for vote in qs:
#                     for w in range(0, vote.userWeight):
#                         valueArray.append(vote.value)
#                 if len(qs) > 0:
#                     value = np.median(valueArray)
#                     weightMatrix[i,j] = value;
#                     weightMatrix[j,i] = 1/value;  
              
    return weightMatrix

def calcCriteriaWeight(criterias, votes):
    return calcWeightVector(calcWeightMatrix(criterias, criterias, votes))

def calcVariantsWeightRespectToCriteria(variants, votes, parentCrit):
    return calcWeightVector(calcWeightMatrix(variants, variants, votes, parentCrit))

def calcCriteriasWeightRespectToVariant(criterias, votes, parentCrit):
    return calcWeightVector(calcWeightMatrix(criterias, criterias, votes, parentCrit))