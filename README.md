# burmese-meitei-alignment
Learning to Parse a Lower-Resource Language, Meitei, through Alignment with a Higher-Resource Language, Burmese.
Science fair research project 2017. in progress.

# usage

1. scrapeData.py:
Used to scrape foreign language data from the web, writes to an htm file.

2. segmenter.py:
Use this to segment Burmese in htm file
based on https://github.com/thantthet/MyanmarParser-Py

3. createEmbeddings.py:
[partially inaccurate, changes being made]
Creates embeddings given an htm file, saves ckpt.
based on https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/tutorials/word2vec/word2vec_basic.py

4. procrustEmbeddings.py:
Reads from 2 ckpt's, aligns the vector spaces, performs k-nearest.
