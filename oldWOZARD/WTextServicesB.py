""" WTextServicesB are basically the same as version A except for the trial support for unicode.
	Consequently, all strings are expected to be unicode versions (u"text" and the like). 
	Especially all regular expressions are compiled with the U flag.
"""

import re
import codecs
from logging import info


class WordList:
	def __init__(self):
		self.stw = {}
	
	def readWordsFromFile(self,filename, encoding="utf-8"):
		nfile = codecs.open (filename,'r',encoding)
		#nfile = codecs.open ("stopwords_en.txt")
		for w in nfile:
			#print w[:(-1)]
			self.stw[w[:(-1)]] = 1		### w[:-1] will be the line (word) without the terminal '\n'
		nfile.close()

	def inList(self,w):
		return w in self.stw

class WTranslator:
	def __init__(self):
		self.repl = []

	def addReplacer(self, pattern, replacement):
		self.repl.append((pattern,replacement))

	def translate(self,s):
		result = s
		for p,r in self.repl:
			tmp = result.replace(p,r)
			result = tmp
		return result
		
	def readPatternsFromFile(self,filename,encoding="utf-8"):
		"""read pattern file (each line of the tabulator separated form: '"pattern"[\t:,;]"patternname"[\n\r]?[\n\r$]' ) and add them to the StringAnalyzer's pattern list."""
		f = codecs.open(filename,"r",encoding)
		r = re.compile(ur'"(.+?)"[\t:;,]"(.+?)"[\n\r]?[\n\r]?',re.U) 
		for l in f:
			#print repr(l)
			m = r.match(l)
			#print m

			if m != None:
				try:
					pat,repl = m.groups()
					self.addReplacer(pat,repl)
				except ValueError:
					print "format error in file %s: %s" % (repr(filename),repr(l))
			else:	
				print "format error in file %s: %s" % (repr(filename),repr(l))
		
		print "WTranslator:readPatternsFromFile ... done"
	

class WRegexpTranslator(WTranslator):
	def __init__(self):
		self.repl = []

	def addReplacer(self, pattern, replacement):
		self.repl.append((re.compile(pattern,re.U),replacement))
		info("[WRegexpTranslator:addReplacer] %s %s" % (repr(pattern),repr(replacement)))

	def translate(self,s):
		result = s
		for re,repl in self.repl:
			#print repl
			tmp = re.sub(repl,result)
			result = tmp
		return result

	def translateN(self,s):
		"""return the rtranslated text as well as the total number of matches in the whole translation process"""
		result = s
		n = 0
		for re,repl in self.repl:
			#print repl
			tmp,nn = re.subn(repl,result)
			n = n+nn
			result = tmp
		return result,n
		

class StringAnalyzer(object):
	def __init__(self):
		## Die parserliste enthaelt fuer jedes Pattern einen regulaeren Ausdruck
		self.parsers = []
		# self.parsers.append(re.compile('TimePositionStamp:'+reListLike(['posx','posy','posz']) ))
		# print 'TimePositionStamp: (?P<zeit>[\d.]*);'+reListLike(['posx','posy','posz'])+';'+reListLike(['look1','look2','look3'])+';'

	def addPattern(self,regexp,patternname):
		self.parsers.append((re.compile(regexp,re.U),patternname))
	
	def countAllPatterns(self,s):
		result = {}
		for rex,name in self.parsers:
			result[name] = len(rex.findall(s))
		return result

	def countAllPatternsList(self,s):
		""" returns a list of counts -- in the same order as the patterns were added """
		result = []
		for rex,name in self.parsers:
			result.append( len(rex.findall(s)) )
		return result	
	

class Counter(object):
	def __init__(self, classify=(lambda x:x)):
		""" counts occurences of objects. a clasifier function is can be provided to categorize or 
			otherwise preprocess objects"""
			
		self.dic = {}
		self.cla = classify
		
	def input(self,obj):
		k = self.cla(obj)		## classify the object -- default is identity
		try:
			self.dic[obj] = self.dic[obj] + 1
		except(KeyError):
			self.dic[obj] = 1

	def getRanking(self):
		items = self.dic.items()
		items.sort(key=(lambda (k,num):num))
		return items
		
	def sortedItems(self):
		items = self.dic.items()
		items.sort(key=(lambda (k,num):k))
		return items
		
	def items(self):
		return self.dic.items()
	
	def objects(self):
		return self.dic.keys()

	def objectsSorted(self):
		return self.dic.keys()

	def counts(self):
		return self.dic.values()
	

#def extractPatternSequence(p,text):
#	"""Returns a sequence of all matches of some pattern"""

def countOccurrences(p,text,fn = (lambda x:x)):
	### For a given pattern p and a text t the function counts all non-overlaping matches of p in t.
	### Different occurences of the one pattern are counted seperately in a
	### fn is a mapping to process the occurence strings before they are send to the counting dictionary (for example lower to make counting insensitive)
	result = {}

	r = re.compile(p,re.U)

	for m in r.finditer(text):
		occ  = fn(text[m.start():m.end()])
		if occ in result:	result[occ] = result[occ] + 1
		else:				result[occ] = 1

	return result

def demoWTranslator():
	s = "Dies ist ein Teststring, in dem gleich alle neue Zeilen\nmit einem > beginnen.\nAusserdem werden Blas durch Blubbs ersetzt."
	print s
	r = WTranslator()
	r.addReplacer("\n","\n>")
	r.addReplacer("Bla","Blubb")
	print (r.translate(s))

def demoWRegexpTranslator():
	s = "<tag>fffff</tag> in dem gleich alle umschliessenden <tag>s durch umschliessende <bla>s ersetzt sind. Der umschlossene Inhalt bleibt gleich."
	print s
	r = WRegexpTranslator()
	r.addReplacer(r"<tag>(f*)</tag>",r"<bla>\1</bla>")
	print (r.translate(s))


def demo():
	demoWTranslator()
	demoWRegexpTranslator()
	print countOccurrences(r"\w+", "dies geraet kann worte zaehlen. Es kann aber mehr als Worte zaehlen, wenn man andere Muster benutzt.")

	
##demo()
