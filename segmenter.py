#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Michelle Yakubek
# see readme for more instructions
# makes use of github.com/thantthet 's code
# see the license in myparser.py for details

from myparser import MyParser
import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

# --------------------

dataFiles = ["MARCH.htm"] # add multiple files to this as needed
exportHTM = "MARCH_break.htm" # new file will be created. if file already exists will append

# --------------------

exportF = codecs.open(exportHTM, mode='a', encoding='utf-8')

m = MyParser()

def segmentAndAppend(stri):
  #stri = u'နေကောင်းရဲ့လား'
  offset = 0
  output = ""
  while offset < len(stri):
    breaktype, next_offset = m.get_next_syllable(stri, len(stri), offset) # parse
    exportF.write(stri[offset:next_offset]+" ") # extract syllable using start offset and end offset
    offset = next_offset

for File in dataFiles:
  with codecs.open(File, mode='r', encoding='utf-8') as input_file:
    line = ''
    while True:
      word, space, line = line.partition(' ')
      if space:
        # A word was found
        # Clean up the word:
        word = word.replace("\n","")
        word = word.replace("/","")
        word = word.replace("|","")
        if len(word)>0:
          segmentAndAppend(word)
      else:
        # A word was not found; read a chunk of data from file
        next_chunk = input_file.read(1000)
        if next_chunk:
          # Add the chunk to our line
          line = word + next_chunk
        else:
          # No more data; yield the last word and return
          exportF.write(word.rstrip('\n')+" ")
          break

exportF.close()
