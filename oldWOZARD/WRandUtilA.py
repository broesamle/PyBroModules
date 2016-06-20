#from random import random
import numpy as np

def getNRandomPairs(text,N=1):
	if len(text)<=2: 	return [ (text,0) for n in range(N) ]
	else:				A = np.random.randint(0,len(text)-2,N)
	return [ (text[a:a+2],a) for a in A ]
	
	
def getRndSlice(s):
	a = np.random.randint(0,len(s)-1,1)
	if a+1 == len(s): 	b = a+1	# hit the last position -- no randomisation necessary (, and possible).
	else: 				b = np.random.randint(a+2,a+10,1)
 	return slice(a,b)

def getRndSliceMinLen(s,minl=1):
	a,b = 0,0
	while b-a < minl:
		a = np.random.randint(0,len(s)-1,1)
		if a+1 == len(s): 	b = a+1	# hit the last position -- no randomisation necessary (, and possible).
		else: 				b = np.random.randint(a+2,a+10,1)
	return slice(int(a),int(b))


def meanF (l,fn = (lambda x:x) ):
	return sum(map(fn,l)) / float(len(l))

def sumF (seq,f=(lambda x:x)):
	return sum (map(f,seq))

def expectedValue (seq,f=(lambda x:x)):
	return sum (map(f,seq)) / float(len(seq))


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

def discreteDistribution(seq):
	res = {}
	for el in seq:
		if el in res:
			res[el] = res[el] +1
		else:
			res[el] = 1
	return res

def weightedChoiceMultIdx(weights,k):
	""" Selects k elements out of a set of elements where the probability of picking the element with index i is weights[i]/sum(weights) the first try.
	the following elements are calculated based on the set of weights reduced by the already chosen ones. ("Urnenmodell ohne oder doch mit??? zuruecklegen") """
	s = "cannot select k=%d elements from %d long sequence." % (k,len(weights))
	if len(weights) < k: raise ValueError( s )

	wei = map(lambda i,x:(i,x), range(len(weights)), weights)
	wsum = sum(weights)

	res = []

	for xx in range(k):
		r = np.random.random()	# random numer [0.0,1.0]
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

def weightedChoiceIdx(weights):
	""" Selects an element out of a set of elements where the probability of picking the element with index i is weights[i]/sum(weights).
		("Urnenmodell ohne zuruecklegen") """
	wsum = sum(weights)
	wnorm = map ( (lambda x: (x/float(wsum))), weights )
	r = np.random.random()
	last = 0
	for i,w in enumerate(wnorm):
		last = last + w
		if r < last: return i
	raise(Except ("Das sollte nicht vorkommen und ist sicher sau-unwahrscheinlich! Wenn es passiert hates etwas mit offenen und geschlossenen Intervallen und Random zu tun!"))
