# -*- coding: iso-8859-15 -*-

### generic helpful list operations and  other functions.

### date: 2008-01-05

import pickle

def pickleToFile (filename,object):
	f = open(filename, "w")
	p = pickle.Pickler(f)
	p.dump(object)
	f.close()
	
def unpickleFromFile (filename):
	f = open(filename,"r")
	return pickle.Unpickler(f).load()

### sigmoid main slope roughly between -1 and 1 
sigmoidWoz = lambda x:1-(1/(1+(2.718281828459**(x*7))))
### standard e sigmoid with no stretch etc.
sigmoid = lambda x:1-(1/(1+(2.718281828459**(x))))

def getSigmoid(x1,x2):
	""" return a lambda function object representing a sigmoid. 
		x1 and x2 mark the lower and upper bound of the relevant input value range
		that is the area where the sigmoid will have considerable slope"""
	d = x2-x1
	thr = (x2+x1) / 2.0
	return lambda x:1-(1/(1+(2.718281828459**((x-thr)*6.0/d)))) 



##############################################################################
### defaults and dictionaries
##############################################################################


def fetchIfNotDef(maybedefined,dictionary,key,default=None,conversion=(lambda x:x)):
	if maybedefined != None:
		result = maybedefined
	else:
		if key in dictionary:
			result = conversion(dictionary[key])
		else:
			result = default
	return result	

def fetchOrDefault(dictionary,key,default=None,conversion=(lambda x:x)):
	if key in dictionary:
		result = conversion(dictionary[key])
	else:
		result = default
	return result

def collapse(e,sep=None):
	"""post hoc interpretation: this function somehow collapses/flattens the internal structure of nested list structures""" 
	if len(e) == 0:
		return e
	else:
		result = e[0][:0]	## pick the first element in e; initialize result with empty sequence according to type of this first element
		for x in e:
			result = result + x
		return result

def collapseSet(e):
	result = set([])
	for s in e:
		result = result | s
	return result

### remove uninterrupted repetitions in sequences
# not generic (strings, lists and tuples are implemented so far)
def removeEchoes(s):
	if len(s) <= 1:
		return s
	else:
		if s[:0] == []:		## if s is a list
			print "list"
			pre = identity
			post = identity
		elif s[:0] == ():	## if s is a tuple
			print "tuple"
			pre = list
			post = tuple
		elif s[:0] == "":	## if s is a tuple
			print "string"
			pre = list
			post = collapse

		result = []

		s = pre(s)				## convert input seq to list if necessary (pre-FN was initialized erlier according to type of seq.)
		result.append(s[0])
		for i in s[1:]:
			if i != result[-1]:
				result.append(i)
		return post(result)		## convert list back to given input type


### make sequences unique (see http://code.activestate.com/recipes/52560/)
### there is some discussion on even more efficient algorithms there. That might help, if elements are not set-member-able
def unique(alist):    # Fastest order preserving
	set = {}
	return [set.setdefault(e,e) for e in alist if e not in set]

def uniqueFast(alist):    # Fastest without order preserving
	set = {}
	map(set.__setitem__, alist, [])
	return set.keys()


def reListLike(
	itemnames,
	intro 		= '\(',
	outtro 		= "\)",
	sep 		= ",",
	element 	= "-?[\d]*.?[\d]*",
	space 		= "\s*" ):
	"""
	Generate RE-String to parse a list-like expression like vectors etc.
	Don't forget to escape special characters in the parameters!
	itemnames:	list of names for each element to parse in the list expression
	intro:		introducing brackets
	outtro: 	closing brackets
	sep:		trennzeichen
	element:	ausdruck zum parsen eines elementes
	space:		RE zum parsen von whitespace

	[DEFAULT: Fliesskomma-Vektoren; z.B. (1, 0.4, -.3, 1.)
	"""

	g1 = '(?P<'
	g2 = '>'
	g3 = ')'

	if len(itemnames) > 0:
		s = space + intro
		for i in itemnames[:-1]:
			s = s + space + g1+i+g2+element+g3 + space + sep
		s = s + space + g1+itemnames[-1]+g2+element+g3 + space + outtro + space
	else:
		s = space + intro + space + outtro + space

	return s


def tabsepList(
	items,
	intro 		= '',
	outtro 		= "\n",
	sep 		= "\t"):
	"""
	Generate a string from a list in the fasion of one line in a tabulator separated file 
	intro:		introducing brackets
	outtro: 	closing brackets
	sep:		trennzeichen
	"""
	if len(items) == 0:		return intro + outtro
	elif len(items) == 1:	return intro + items[0] + outtro
	
	s = intro + items[0]
	for i in items[1:]:
		s = s + sep + i
		
	return s + outtro


################################
### some randomization stuff ###
################################


def maxIdx(l):
	a = l[0]
	max_idx = 0
	for i,el in enumerate(l):
		if el > a:
			a = el
			max_idx = i
	return max_idx

def unzip(l):
	A = []
	B = []
	for a,b in l:
		A.append(a)
		B.append(b)
	return A,B

def unzipN(l):
	if len(l) == 0:
		raise ValueError("Cannot generically unzip empty sequence.")
	ress = ()
	for i in l[0]:
		ress = ress+ ([],)

	for i in l:
		for idx,j in enumerate(i):
			ress[idx].append(j)
	return ress
	

   ### kann man generisch loesen: 1. element auslesen, durchiterieren und entsprechend viele listen mit je 1 element erzeugen
   ### danach jedes weitere durchiterieren und jeweils elemente anhaengen.
