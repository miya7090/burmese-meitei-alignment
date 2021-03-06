# Michelle Yakubek
# creates embeddings given htm file
# see readme for more instructions

# ==============================================================================

# RUN chcp 65001 in cmd line first!

# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import os
import random
import zipfile

import numpy as np
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from bs4 import BeautifulSoup
import codecs

import pickle

#######################################

dataFiles = ["MARCH_break.htm"] # add multiple files to this as needed
batch_size = 128
embedding_size = 128  # Dimension of the embedding vector.
vocabulary_size = 4000 # number of most common words to keep
num_steps = 12001 #checkpoints at 2000
pathforsaving = "EMBEDS_march/run_one.ckpt"
embeddingF = "embeds_march.p"
dictName = "march_dict.p"
revDictName = "march_rev_dict.p"
#######################################

words = []

fileNo = 0;
for File in dataFiles:
  fileNo = fileNo+1
  print("going through file "+str(fileNo)+"...\n")
  with codecs.open(File, mode='r', encoding='utf-8') as input_file:
    line = ''
    while True:
      word, space, line = line.partition(' ')
      if space:
        # A word was found
        word = word.replace("\n","")
        word = word.replace("/","")
        word = word.replace("|","")
        if len(word)>0:
          words.append(word)
      else:
        # A word was not found; read a chunk of data from file
        next_chunk = input_file.read(1000)
        if next_chunk:
          # Add the chunk to our line
          line = word + next_chunk
        else:
          # No more data; yield the last word and return
          words.append(word.rstrip('\n'))
          break

print('Data size', len(words))


# Step 2: Build the dictionary and replace rare words with UNK token.
def build_dataset(words):
  # array of the most common instances, word|frequency
  count = [['UNK', -1]]
  count.extend(collections.Counter(words).most_common(vocabulary_size - 1))
  
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary) # create indices for the words ordered by frequency

  data = list()
  unk_count = 0

  data.append(0)
  data.append(0)
  data.append(0) #debugging, don't remove
  for word in words:
    if word in dictionary: # if it's one of the most common words
      index = dictionary[word] # point it to same location in dictionary
      data.append(index) # create array of indices
    else:
      index = 0  # point it to dictionary['UNK']
      unk_count += 1 # count unknowns this way since not counted by Counter
  count[0][1] = unk_count
  
  reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  return data, count, dictionary, reverse_dictionary

data, count, dictionary, reverse_dictionary = build_dataset(words)
del words  # not needed
print('Most common words (+UNK)', count[:15])
print('Sample data', data[:10], [reverse_dictionary[i] for i in data[:10]])

pickle.dump(dictionary, open(dictName,"wb"))
pickle.dump(reverse_dictionary, open(revDictName,"wb"))

# Step 3: Function to generate a training batch for the skip-gram model.

data_index = 0

def generate_batch(batch_size, num_skips, skip_window):
  global data_index
  assert batch_size % num_skips == 0
  assert num_skips <= 2 * skip_window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  span = 2 * skip_window + 1  # [ skip_window target skip_window ]
  buffer = collections.deque(maxlen=span)
  for _ in range(span):
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  for i in range(batch_size // num_skips):
    target = skip_window  # target label at the center of the buffer
    targets_to_avoid = [skip_window]
    for j in range(num_skips):
      while target in targets_to_avoid:
        target = random.randint(0, span - 1)
      targets_to_avoid.append(target)
      batch[i * num_skips + j] = buffer[skip_window]
      labels[i * num_skips + j, 0] = buffer[target]
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  return batch, labels

batch, labels = generate_batch(batch_size=8, num_skips=2, skip_window=1)
for i in range(8):
  print(batch[i], reverse_dictionary[batch[i]],
        '->', labels[i, 0], reverse_dictionary[labels[i, 0]])
        #Error?????????????? above does not work??????????????????

# Step 4: Build and train a skip-gram model.

skip_window = 1       # How many words to consider left and right.
num_skips = 2         # How many times to reuse an input to generate a label.

# We pick a random validation set to sample nearest neighbors. Here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 16     # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = np.random.choice(valid_window, valid_size, replace=False)
num_sampled = 64    # Number of negative examples to sample.

graph = tf.Graph()

with graph.as_default():

  # Input data.
  train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
  train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
  valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

  # Ops and variables pinned to the CPU because of missing GPU implementation
  with tf.device('/cpu:0'):
    # Look up embeddings for inputs.
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)

    # Construct the variables for the NCE loss
    nce_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size],
                            stddev=1.0 / math.sqrt(embedding_size)))
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

  # Compute the average NCE loss for the batch.
  # tf.nce_loss automatically draws a new sample of the negative labels each
  # time we evaluate the loss.
  loss = tf.reduce_mean(
      tf.nn.nce_loss(weights=nce_weights,
                     biases=nce_biases,
                     labels=train_labels,
                     inputs=embed,
                     num_sampled=num_sampled,
                     num_classes=vocabulary_size))

  # Construct the SGD optimizer using a learning rate of 1.0.
  optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

  # Compute the cosine similarity between minibatch examples and all embeddings.
  norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
  normalized_embeddings = embeddings / norm
  valid_embeddings = tf.nn.embedding_lookup(
      normalized_embeddings, valid_dataset)
  similarity = tf.matmul(
      valid_embeddings, normalized_embeddings, transpose_b=True)
  
  # Add variable initializer.
  init = tf.global_variables_initializer()
  
  # Add saver variable
  saver = tf.train.Saver()
  
# Step 5: Begin training.

with tf.Session(graph=graph) as session:
  # We must initialize all variables before we use them.
  init.run()
  print("Initialized")
  
  save_path = saver.save(session, pathforsaving)
  print("Saving to path:", save_path)

  average_loss = 0
  for step in xrange(num_steps):
    batch_inputs, batch_labels = generate_batch(
        batch_size, num_skips, skip_window)
    feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

    # We perform one update step by evaluating the optimizer op (including it
    # in the list of returned values for session.run()
    _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
    average_loss += loss_val

    if step % 2000 == 0:
      if step > 0:
        average_loss /= 2000
      # The average loss is an estimate of the loss over the last 2000 batches.
      print("Average loss at step ", step, ": ", average_loss)
      average_loss = 0

    # Note that this is expensive (~20% slowdown if computed every 500 steps)
    '''
    if step % 10000 == 0:
      sim = similarity.eval()
      for i in xrange(valid_size):
        valid_word = reverse_dictionary[valid_examples[i]]
        top_k = 8  # number of nearest neighbors
        nearest = (-sim[i, :]).argsort()[1:top_k + 1]
        log_str = "Nearest to %s:" % valid_word
        for k in xrange(top_k):
          close_word = reverse_dictionary[nearest[k]]
          log_str = "%s %s," % (log_str, close_word)
        print(log_str)
    '''
  final_embeddings = normalized_embeddings.eval()
  pickle.dump(final_embeddings, open(embeddingF,"wb"))

#visualizer removed
