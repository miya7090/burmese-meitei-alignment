# procrustes analysis finds an alignment between two vector spaces
# this takes in embeddings from two languages and aligns them
# in progress...
# - Michelle Yakubek

from scipy.spatial import procrustes
import numpy as np
import tensorflow as tf
import math
import pickle


firstDict = pickle.load(open("meiteiDict.p","rb"))
firstRevDict = pickle.load(open("meiteiRevDict.p","rb"))
secondDict = pickle.load(open("networkDict.p","rb"))
secondRevDict = pickle.load(open("networkRevDict.p","rb"))

### Variables ###

# The size of the matrices
vocabulary_size = 6000 # number of words analyzed
embedding_size = 128  # dimension of the embedding
firstLocation = "meitei_embeddings/run_one.ckpt" # location that tensorflow saved the embedding to
secondLocation = "network_embeddings/run_one.ckpt" # ditto for the second embedding

### Initialization ###

graph = tf.Graph()

with graph.as_default():
  with tf.device('/cpu:0'):
    # initialize an embedding variable of zeros
    embeddings = tf.Variable(tf.random_uniform([vocabulary_size, embedding_size], 0, 0))

  saver = tf.train.Saver()

### Embedding retrieval + Procrustes ###

with tf.Session(graph=graph) as sess:
  print("retrieving language 1 embeddings...")
  saver.restore(sess, firstLocation) # overwrites embeddings
  #print("embedding for 1: ",type(sess.run(embeddings)))
  firstLang = sess.run(embeddings) # the embeddings from the first language
  
  print("retrieving language 2 embeddings...")
  saver.restore(sess, secondLocation) # overwrites embeddings
  #print("embedding for 2: ",type(sess.run(embeddings)))
  secondLang = sess.run(embeddings) # the embeddings from the second language
  
  # running procrustes from scipy
  mtx1, mtx2, disparity = procrustes(firstLang, secondLang)
  # mtx1: standardized data1
  # mtx2: data2 oriented to fit data1
  # disparity: difference between these sets, sum((data1-data2)^2)
  print(mtx1)
  print(mtx2)
  print(disparity)

###############plotting
'''
def plot_with_labels(low_dim_embs, labels, filename='tsneProcrustx.png'):
  assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
  plt.figure(figsize=(18, 18))  # in inches
  matplotlib.rc('font', family='Zawgyi-One')
  for i, label in enumerate(labels):
    x, y = low_dim_embs[i, :]
    plt.scatter(x, y)
    try:
        label = str(label,'utf-8')
    except:
        label = label
    plt.annotate(label,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

  plt.savefig(filename)

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
plot_only = 500
low_dim_embs = tsne.fit_transform(mtx1[:plot_only, :])
labels = [firstRevDict[i] for i in range(plot_only)]
plot_with_labels(low_dim_embs, labels)
'''
##################neighbors
from sklearn.neighbors import NearestNeighbors

for j in range(32):
  print("closest to ", firstRevDict[j])
  
  with open("translations.txt", "a") as myfile:
    myfile.write("closest in meitei to ")
  with open("translations.txt", "ab") as myfile:
    myfile.write(firstRevDict[j].encode("utf-8"))
  with open("translations.txt", "a") as myfile:
    myfile.write("\n\n")
    
  neigh = NearestNeighbors(4) # find the k nearest words
  neigh.fit(mtx2)                                     ##
  dist, ind = neigh.kneighbors([mtx1[j]]) # find neighbors

  for i, index in enumerate(ind[0]):
    print("index:",ind[0][i])
    print("value:", secondRevDict[index])                    ##
    print("distance:",dist[0][i])

    with open("translations.txt", "a") as myfile:
      myfile.write("I:"+str(ind[0][i])+"\nW:")
    with open("translations.txt", "ab") as myfile:
      myfile.write(secondRevDict[index])    ## may or may not need .encode("utf-8")
    with open("translations.txt", "a") as myfile:
      myfile.write("\nD:"+str(round(dist[0][i],3))+"\n\n")

