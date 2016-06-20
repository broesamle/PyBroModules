### generic helpful list operations and  other functions.

identity = lambda x:x


def collapse(e,sep=None):
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

### create strings for regular expressions in a non-ctryptic manner

def reListLike(
	itemnames,
	intro 		= '\(', outtro ="\)",
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


