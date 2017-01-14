# procrustes analysis finds an alignment between two vector spaces
# this takes in embeddings from two languages and aligns them
# in progress...
# - Michelle Yakubek

from scipy.spatial import procrustes
import numpy as np
import tensorflow as tf
import math

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
  
  # do stuff (in progress)