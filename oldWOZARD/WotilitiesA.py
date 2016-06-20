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


identity = lambda x:x

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


##############################################################################
### iterable and sequential stuff
##############################################################################





#class IterList(object):
#	def __init__(self,list,fn=identity):
#		self.l = list
#		self.i = 0
#		self.size = len(list)
#	
#	def __iter__(self):
#		return self
#		
#	def next(self):
#		self.i = self.i + 1 
#		if self.i > self.size:
#			raise(StopIteration)
#		return self.l[self.i-1]
#
#class IterDict(IterList):
#	def __init__(self,keys,dict,**kwds):
#		IterList.__init__(self,keys,**kwds)
#		self.dict = dict
#
#	def next(self):
#		ne = IterList.next(self)
#		return self.dict[ne]


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

def meanF (l,fn = identity ):
	return sum(map(fn,l)) / float(len(l))


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


##############################################################################
### some generic list functions with parameterized evaluation Functions
##############################################################################
#def maxF (seq,f=identity):
#	return max (map(f,seq))

#def maxF (seq,f=identity):
#	return min (map(f,seq))

def sumF (seq,f=identity):
	return sum (map(f,seq))

def expectedValue (seq,f=identity):
	return sum (map(f,seq)) / float(len(seq))


###############################
## generic list like output
###############################

# def genericListOutput(
# 	elements,
# 	intro 		= '[',
# 	outtro 		= ']',
# 	sep 		= ",",
# 	itemnames)
# 	"""generic list like output"""
# 
# 	if len(itemnames) > 0:
# 		s = intro
# 		for i in elements[:-1]:
# 			s = s + element + sep
# 		s = s + itemnames[-1] + outtro
# 	else:
# 		s = intro + outtro
# 	return s

#######################################################################
### create strings for regular expressions in a non-cryptic manner ###
#######################################################################

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

from random import random


def weightedChoiceIdx(weights):
	""" Selects an element out of a set of elements where the probability of picking the element with index i is weights[i]/sum(weights).
		("Urnenmodell ohne zuruecklegen") """
	wsum = sum(weights)
	wnorm = map ( (lambda x: (x/float(wsum))), weights )
	r = random()
	last = 0
	for i,w in enumerate(wnorm):
		last = last + w
		if r < last: return i
	raise(Except ("Das sollte nicht vorkommen und ist sicher sau-unwahrscheinlich! Wenn es passiert hates etwas mit offenen und geschlossenen Intervallen und Random zu tun!"))

from copy import copy


def weightedChoiceMultIdx(weights,k):
	""" Selects k elements out of a set of elements where the probability of picking the element with index i is weights[i]/sum(weights) the first try.
	the following elements are calculated based on the set of weights reduced by the already chosen ones. ("Urnenmodell ohne oder doch mit??? zuruecklegen") """
	s = "cannot select k=%d elements from %d long sequence." % (k,len(weights))
	if len(weights) < k: raise ValueError( s )

	wei = map(lambda i,x:(i,x), range(len(weights)), weights)
	wsum = sum(weights)

	res = []

	for xx in range(k):
		r = random()	# random numer [0.0,1.0]
		rr = r * wsum
		last = 0
		for i,(oidx,w) in enumerate(wei):
			last = last + w
			if rr < last:
				res.append(oidx)
				del wei[i]		# remove the chosen element
				wsum = wsum -w	# reduce wsum accordingly
				break
	return res

def discreteDistribution(seq):
	res = {}
	for el in seq:
		if el in res:
			res[el] = res[el] +1
		else:
			res[el] = 1
	return res
	
def maxIdx(l):
	a = l[0]
	max_idx = 0
	for i,el in enumerate(l):
		if el > a:
			a = el
			max_idx = i
	return max_idx


### seems to calculate the expected sum of fetching a k-element sample from a population of values
# tested in some experiments and considered plausible. ;-) Woz.
# expected value when making a sample of k elements from the population pop.
# ev is the evaluation function and defaults to the identity
def expected(pop,k,ev=(lambda x:x)):
	all = sum(map(ev,pop))
	n = len(pop)

	res = 0
	for i in range(k):
		e = float(all) / n
		res = res + e
		all = all - e
		n = n - 1
	return res



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
