# Michelle Yakubek
# web scraper
# see readme for more instructions

# starts out with foreign-language sites, finds links to other foreign-language sites, etc
# saves to an htm file, also writes to log/site files

# may need to run chcp 65001 in command line first

'''
to-do list:
 - check for html content before checking if foreign
 - allow parent sites
 - normalize fonts
 - don't read sites with #s etc in the url
 - give up on sites that take too long!
 - delay link cutoff
 - change linkhistoryread so checks all prefixes, other forms
'''

from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import urllib.request

import zipfile

from bs4 import BeautifulSoup
import codecs

from time import strftime, localtime

# --SETTINGS------------------------------------------------------------
nameFile = "MARCH" #will write to an htm file of this name
myURL = ["http://myanmarhealthcentre.com",
"http://www.bbc.com/burmese/",
"http://www.rfa.org/burmese/",
"http://www.myanmar-network.net/",
"http://burmese.voanews.com/",
"https://linlattayar.wordpress.com/",
"http://ohnthar.blogspot.com/",
"https://www.myanmarload.com/",
"http://www.wutyeefoodhouse.com/",
"http://linletkyalsin.blogspot.com/",
"http://www.kamayutmedia.com/",
"https://www.jw.org/mya/",
"http://hivinfo4mm.org/",
"http://www.myanmarwebdesigner.com/blog/",
"http://burmese.dvb.no/dvblive",
"http://soccermyanmar.com/",
"http://www.yatanarpon.com.mm/",
"http://www.news-eleven.com/"] #parent sites to go off of
maxPages = 100000000 # google search with "site:xxxyoururlxxx" beforehand to get an idea
linkHistoryRead = "none" # "none" or "xxxx.txt", will not access these sites (bug: only checks for the exact URL)
# ----------------------------------------------------------------------


log_file = open(nameFile+"Log.txt", "a")
site_file = open(nameFile+"Sites.txt", "a")

def paw(cont): # print and write
	try:
		print(cont)
		log_file.write(cont)
	except:
		print("[error utf8]")
		log_file.write("\n[error utf8]\n")

class LinkParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for (key, value) in attrs:
				if key == 'href':
					newUrl = parse.urljoin(self.baseUrl, value)
					# add it to the colection of links:
					self.links = self.links + [newUrl]

	def getLinks(self, url):
		self.links = []
		self.baseUrl = url
		response = urlopen(url)
		if response.getheader('Content-Type')=='text/html' or response.getheader('Content-Type')=='text/html; charset=UTF-8' or response.getheader('Content-Type')=='text/html; charset=utf-8': # if html page
			htmlBytes = response.read()
			htmlString = htmlBytes.decode("utf-8")
			self.feed(htmlString) #finding links in the data...
			return self.links
		else:
			paw("F:T"+response.getheader('Content-Type'))
			return

#checkPastHave makes sure that we don't download the same page twice
def checkPastHave(potential, alreadys):
	for haveLinked in alreadys:
		if potential == haveLinked:
			return True
	return False
	
def foreign(stringtxt, thresh, strict=False):
	romanCount = 0
	burmeseCount = 0
	# romans in 65-90, 97-122
	# burmese in 4096-4255
	for m in stringtxt:
		c = ord(m)
		if c>4096:
			if c<4255:
				burmeseCount = burmeseCount+1
		elif c<122:
			if c>65:
				if c<90:
					romanCount = romanCount+1
				elif c>97:
					romanCount = romanCount+1
	if burmeseCount == 0 and romanCount == 0:
		return False # not burmese, no div by 0
	fRatio = burmeseCount/(romanCount+burmeseCount)
	if strict:
		paw("|"+str(round(fRatio*100,1))+"%b")
	return (fRatio>thresh)

def deleteRomans(stringtxt):
	words = stringtxt.split()
	try:
		for i, word in enumerate(words):
			if foreign(i-1, 0.8): # if word is foreign
				if not foreign(words[i], 0.8) and not foreign(words[i+1], 0.8) and not foreign(words[i+2], 0.8) and not foreign(words[i+3], 0.8) and not foreign(words[i+4], 0.8) and not foreign(words[i+5], 0.8):
				# if next six words are also foreign
					j = 0 # max english string
					while j<100 and not foreign(words[i+j], 0.8):
						words[i+j] = ""
						j = j+1 # get rid of j if deletion
	except:
		if i>len(words):
			return " ".join(words)
	return " ".join(words)

#processAndWriteData accesses the url, makes a soup, gets raw text, and writes to a file
def processAndWriteData(url):
	with urllib.request.urlopen(url) as response:
		r = response.read()
	soup = BeautifulSoup(r, "html.parser")
	
	[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])] #clean up
	souptxt = soup.get_text()
	
	#check is foreign
	if not foreign(souptxt, 0.5, True):
		paw("\nE")
		raise Exception('not foreign')
		
	edittxt = deleteRomans(souptxt)
	# refine a bit more? #to-do
	soupbytes = edittxt.encode("utf-8")
	with open(nameFile+".htm", "ab") as myfile:
		myfile.write(soupbytes)
		# maybe write to compressed file? #to-do
		
def spider(url):
	pagesToVisit = []
	for link in url:
		pagesToVisit.append(link)
	pagesExtAlready = []
	if linkHistoryRead != "none":
		with open(linkHistoryRead, 'r') as past:
			for line in past.readlines():
				pagesExtAlready.append(line)
	print(pagesExtAlready)
	numberVisited = 0
	numberSuccessfulVisited = 0

	while numberSuccessfulVisited < maxPages and numberVisited<len(pagesToVisit):
		url = pagesToVisit[numberVisited]
		paw(url+strftime("|%H:%M"))
		numberSuccessfulVisited = numberSuccessfulVisited +1
		numberVisited = numberVisited +1
		
		try:
			processAndWriteData(url)
			parser = LinkParser()
			links = parser.getLinks(url) # get all the links on that webpage
			#print(links)
			for toLink in links: # check if those links are valid
				if checkPastHave(toLink, pagesToVisit) == False:
					if checkPastHave(toLink, pagesExtAlready) == False: #if haven't visited
						pagesToVisit.append(toLink)
			paw("\n"+str(numberVisited)+"|"+str(numberSuccessfulVisited)+"/"+str(len(pagesToVisit))+"\n")
			site_file.write(url+"\n")
		except:
			numberSuccessfulVisited = numberSuccessfulVisited-1

		
spider(myURL)
log_file.close()
