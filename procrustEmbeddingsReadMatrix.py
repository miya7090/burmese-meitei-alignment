# Michelle Yakubek
# see readme for more instructions

from scipy.spatial import procrustes
import numpy as np
import tensorflow as tf
import math
import pickle
import random

### Variables ###
# The size of the matrices
vocabulary_size = 6000 # number of words analyzed
embedding_size = 128  # dimension of the embedding
'''
firstDict = pickle.load(open("meiEmbedDict.p","rb"))
firstRevDict = pickle.load(open("meiEmbedRevDict.p","rb"))
secondDict = pickle.load(open("allEmbedDict.p","rb"))
secondRevDict = pickle.load(open("allEmbedRevDict.p","rb"))
firstMatrix = pickle.load(open("meiEmbed.p","rb")) # location that tensorflow saved the embedding to
#secondMatrix = pickle.load(open("allEmbed.p","rb")) # ditto for the second embedding
secondMatrix = np.random.uniform(size=(6000,128))
'''

firstDict = pickle.load(open("april_dict.p","rb"))
firstRevDict = pickle.load(open("april_rev_dict.p","rb"))
firstMatrix = pickle.load(open("embeds_april.p","rb")) # location that tensorflow saved the embedding to
secondDict = pickle.load(open("march_dict.p","rb"))
secondRevDict = pickle.load(open("march_rev_dict.p","rb"))
secondMatrix = pickle.load(open("embeds_march.p","rb")) # ditto for the second embedding
#firstMatrix = np.random.uniform(1.000, 1.001, size=(6000,128))
FL = "distances_beta.txt" # distances
FFL = "translations_beta.txt" # "translations"

### Procrustes ###
mtx1, mtx2, disparity = procrustes(firstMatrix, secondMatrix)
mtx1 = firstMatrix
mtx2 = secondMatrix
# mtx1: standardized data1
# mtx2: data2 oriented to fit data1
# disparity: difference between these sets, sum((data1-data2)^2)
print(mtx1)
print(mtx2)
print(disparity*100)

##################neighbors
from sklearn.neighbors import NearestNeighbors

j = 0
for LLL in range(30):
  if LLL < 6:
    j = LLL
  elif LLL < 18:
    j=random.randint(5, 100)
  else:
    j=random.randint(100, 500)
    
  with open(FL, "a") as myfile:
    myfile.write("\n")
  with open(FL, "ab") as myfile:
    myfile.write(firstRevDict[j].encode("utf-8"))
  with open(FL, "a") as myfile:
    myfile.write(",")
    
  neigh = NearestNeighbors(4)             # find the k nearest words
  neigh.fit(mtx2)                                     ##
  dist, ind = neigh.kneighbors([mtx1[j]]) # find neighbors

  for i, index in enumerate(ind[0]):
    with open(FL, "ab") as myfile:
      myfile.write(secondRevDict[index].encode("utf-8"))    ## may or may not need .encode("utf-8")
    with open(FL, "a") as myfile:
      myfile.write(",")
      
      
'''
for j in range(32):
  print("closest to ", firstRevDict[j])
  
  with open(FFL, "a") as myfile:
    myfile.write("closest in meitei to ")
  with open(FFL, "ab") as myfile:
    myfile.write(firstRevDict[j].encode("utf-8"))
  with open(FFL, "a") as myfile:
    myfile.write("\n\n")
    
  neigh = NearestNeighbors(4) # find the k nearest words
  neigh.fit(mtx2)                                     ##
  dist, ind = neigh.kneighbors([mtx1[j]]) # find neighbors

  for i, index in enumerate(ind[0]):
    #print("index:",ind[0][i])
    print("value:", secondRevDict[index])                    ##
    print("distance 1000x:",1000*dist[0][i])

    #with open(FFL, "a") as myfile:
      #myfile.write("I:"+str(ind[0][i])+"\nW:")
    with open(FFL, "ab") as myfile:
      myfile.write(secondRevDict[index].encode("utf-8"))    ## may or may not need .encode("utf-8")
    with open(FFL, "a") as myfile:
      myfile.write("\nD1000:"+str(round((dist[0][i]*1000),3))+"\n\n")
      
'''
