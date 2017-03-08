# Burmese-Meitei Alignment

Learning to Parse a Lower-Resource Language, Meitei, through Alignment with a Higher-Resource Language, Burmese.

Research project 2017.

This software will scrape a large foreign-language corpus from the web, segment it, create word embeddings for it, and perform Procrustes and other analysis upon it in order to generate a usable linguistic model.



# Setup

## PREREQUISITES

1. [Anaconda 4.3.0 - Python 3.6](https://www.continuum.io/downloads)

2. [TensorFlow](https://www.tensorflow.org/install/)

3. [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)

4. htm file of segmented comparison data



## SCRAPING

1. run the scraper `scrapeData` in its directory: `python scrapeData.py`

> this will begin Burmese scraping with existing settings, and will create 3 files: `MARCH.htm`, `MARCHLog.txt`, `MARCHSites.txt`

## SEGMENTING

### Option A

1. install segmenter (Wunna Ko Ko et al): [MMNLP Syllable Breaker](http://myanmarnlpteam.blogspot.com/2008/02/syllable-segmentation-software.html)

2. create a copy of `MARCH.htm` named `MARCH.txt`

3. run MMNLP upon it- choose either `Orthographic Syllable Break` or `Phonological Syllable Break`

4. create a copy of `MARCH_break.txt` named `MARCH_break.htm`

### Option B

1. run the `segmenter` in its directory: `python segmenter.py`

> based on [MyanmarParser-Py](https://github.com/thantthet/MyanmarParser-Py)

> this will segment `MARCH.htm` and create the file `MARCH_break.htm`

## EMBEDDING

> based on [basic 
word2vec](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/tutorials/word2vec/word2vec_ba
sic.py)

> this will create embeddings from `MARCH_break.htm` and will save a pickled embedding `embeds_march.p` and two dictionaries, `march_dict.p` and `march_rev_dict.p`

1. create a directory `EMBEDS_march` that the variable `pathforsaving` can use
2. run the embedder `createEmbeddings` in its directory: `python createEmbeddings.py`

3. modify the embedder for your comparison data so it creates embeddings from `APRIL_break.htm`, saves to "april" files, etc.

4. create a directory `EMBEDS_april`

5. run the program again: `python createEmbeddings.py`

## PROCRUSTES

1. modify `procrustEmbeddingsReadMatrix` as needed to produce the needed data

2. run procrustes in its directory: `python procrustEmbeddingsReadMatrix.py`



