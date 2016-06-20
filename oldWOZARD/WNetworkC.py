#
#  WNetworkB.py
#  
#
#  Created by martinb on 7.02.2008.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#

#
#  WNetworkA.py
#  
#
#  Created by martinb on 5.02.2008.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#
import os

from WotilitiesA import tabsepList, IterDict
import random

class IterConnections(object):
	def __init__(self,nodes,succwei):
		self.nodes = nodes	## maps ids to nodes.
		self.succwei = succwei
		
		self.n = None			## current node
		self.i = 0				## index in nodes
		self.nodesN = len(nodes)
		self.currSucc = []	## dictionary with all successors of current node

	def __iter__(self):
		return self
	
	def next(self):
		if len(self.currSucc) == 0:
			### no successors in current successor list
			### -> proceed to next node and refill successor list
			self.i += 1 
			if self.i > len(self.nodes):
				raise(StopIteration)
			self.n = self.nodes[self.i-1] 	
			self.currSucc = self.succwei[self.n].copy()
			return self.next()
		else:
			m,w = self.currSucc.popitem()
			return (self.n,m,w)
			


class ActNet(object):
	""" Activation networt using dictionaries for predeceding and succeding nodes respectively.
	please note that deleting nodes will be quite some efford. 
	adding them or changing connection weights should be efficient in sparse networks however."""

	def __init__(self, loss=1.0, decay=0.5, cutoffWeight=0.01, strenThreshold=0.01):

		self.similStren = (lambda x,y : (x*y)**2)
		self.decayFn = (lambda x: x * decay)

		maxAct=1.0		### these values should not be changed in the current implementation
		minAct=0.0		### the simultaneous activation strengthening mechanism assumes activation in this interval!

		self.l = loss
		self.Amin = minAct
		self.Amax = maxAct
		
		self.Wcutoff = cutoffWeight		### connection weights below will be treated as zero, 
										### e.g. their connection list entries will be deleted.
										
		self.strenThr = strenThreshold		### changes in connection strength below this value will not be considered 

	# # # maybe we don't need all these indicis in the end :-)
	# # # nodes for example ! ! !

		self.nextID = 0
		self.ids = {}			### maps nodes to numeric IDs (numbers in order of insertion) 
		self.nodes = {}			### maps IDs to nodes
		self.act = {}			### maps nodes to activation levels
		
		# #self.succ = {}			### list of successors for each node ([])
		self.succwei = {}		### dict of connection weights going out to the successors
		
		# #self.pred = {}			### list of predecessors for each node ([])
		# #self.predwei = {}		### list of weights of the connections incoming from the predecessors
		self.sortedNodes = []

	####################################################
	## iterables for network elements 
	####################################################
	def iterNodes(self):
		return self.sortedNodes

	def iterConnections(self):
		""" returns an iterable object; items of the form (n,m,w); n,m are nodes; w is the weight of the
			connection. Connections with w < cutoffWeight are not returned"""
		i = IterConnections(self.nodes,self.succwei)
		print ((i,type(i)))
		return i
	
	def iterActivations(self):
		return IterDict(self.sortedNodes,self.act)
		

	####################################################
	## manage nodes 
	####################################################
	def present(self,n):
		return n in self.act
		
	def addNode(self,n):
		""" Adds a single node identified by n. 
		It will not be connected to any othe node and have activation 0.0, initially."""
		
		if self.present(n):
			raise ValueError, ("ActNetwork:addNode(): node %s already in network" % n)
		
		self.ids[n] = self.nextID
		self.nodes[self.nextID] = n
		self.nextID = self.nextID + 1
		self.act[n] = 0.0
		# #self.succ[n] = {}
		self.succwei[n] = {}
		# #self.pred[n] = [] 
		# #self.predwei[n] = []
		
		print ("adding node %s" % n)
		self.sortedNodes.append(n)

	def addNodes(self, nlist):
		for n in nlist:
			self.addNode(n)
			
	####################################################
	## manage activation
	####################################################
	def maximizeAct(self,n):
		self.setAct(n,self.Amax)
		
	def minimizeAct(self,n):
		self.setAct(n,self.Amin)
		
	def earthAll(self):
		""" Remove all Activation from the Network, e.g. set the activation of all nodes to self.Amin"""
		for k in self.act.keys():
			self.act[k] = self.Amin
	
	def setAct(self, n, act):
		self.act[n] = act
		
	def setActMult(self, nlist, act):
		for n in nlist: 
			self.activateNode(n,act)
			
	def changeAct(self, n, amount):
		self.act[n] = self.act[n] + amount
		
	def changeActBound(self, n, amount):
		self.act[n] = self.act[n] + amount
		if		self.act[n] > self.Amax:	self.act[n] = self.Amax
		elif	self.act[n] < self.Amin:	self.act[n] = self.Amin
		
	def decay(self):
		for n in self.act.iterkeys():
			self.act[n] = self.decayFn(self.act[n])
			
	
	
	####################################################
	## neighbours etc
	####################################################
	def successors(self, n):
		return self.succ[n].keys()
	
	# #def predOf(self, n):
	# #	return self.pred[n]
		
	# #def neighboursOf(self, n):
	# #	return succOf(n) + predOf(n) 

	####################################################
	####################################################
	def deleteConn(self,n,m):
		""" Conceptually, this means to reduce the connection weight to zero. 
			Technically, it means to remove the entry in the respective successor dictionary."""

		if not (self.present(n) and self.present(m)):
			raise ValueError, ("ActNetwork:deleteConn(%s,%s): node not in network" % (n,m))
			
		### a should be the node with the smaller id (which was inserted earlier.)
		### technically, each node originates at the node which was inserted earlier
		### its weight entry is also in the successor dictionary of this earlier node
		if self.ids[n] < self.ids[m]:
			a,b = n,m
		else:
			a,b = m,n
			
		### a -> b
		
		### successors of a
		if b in self.succwei[a]:
			## in this case the connection exists
			# #del self.succ[a][b]
			del self.succwei[a][b]
					
	####################################################
	####################################################
	def setWeight(self,n,m,w):
		""" sets the weight between two nodes n and m. although the network might be nondirectional,
		for each edge it is determined internally which node is predecessor of the other. (based on the numeric ID)"""

		### for performance reasons the weight is holded twice: once in the successor list of a 
		# and once in the predecessor list of b. this makes possible the easy access of input weights as well as output 
		# at each node

		if w < self.Wcutoff:
			self.deleteConn(n,m)
			return
			
		### a should be the node with the smaller id (which was inserted earlier.)
		### connections technically run in this direction: a -> b
		if self.ids[n] < self.ids[m]:
			a,b = n,m
		else:
			a,b = m,n
			
		self.succwei[a][b] = w


	def getWeight(self,n,m):
		""" returns the weight between two nodes n and m."""
			
		### a should be the node with the smaller id (which was inserted earlier.)
		### connections technically run in this direction: a -> b
		if self.ids[n] < self.ids[m]:
			a,b = n,m
		else:
			a,b = m,n
			
		if b in self.succwei[a]:
			return self.succwei[a][b]
		else: 
			return self.Amin

	def changeWeight(self,n,m,amount):
		""" increases (or decreases if amount < 0.0) the weight between two nodes n and m."""
			
		### a should be the node with the smaller id (which was inserted earlier.)
		### connections technically run in this direction: a -> b
		if self.ids[n] < self.ids[m]:
			a,b = n,m
		else:
			a,b = m,n
			
		if b in self.succwei[a]:
			self.succwei[a][b] = self.succwei[a][b] + amount
		else: 
			self.succwei[a][b] = amount
			
		if self.succwei[a][b] < self.Wcutoff:
			del self.succwei[a][b]
			
			

	def strenSimultAct(self):
		""" Strengthen the connection weight between simultaneously activated nodes. 
			For two nodes n,m the weight increase is (A(n)*A(m))**2."""
		
		## act: the list of all nodes with sufficiently high activation to reach a relevant weight increase.
		## we only have to consider nodes n with A(n) > self.strenThr. Activations can be 1.0 at maximum 
		## and we cannot get strengthening differences d > self.strenThr with one (or both) node activations below 
		## that threshold.   
		act = filter(lambda (n,a): a > self.strenThr, self.act.items() ) 
		#tmp = {}
		#for n,a in act:	
		#	tmp[n] = a
		#act = tmp
		
		while act != []:  
			n,an = act[0]
			del act[0]		## we do not need this node in act any more as it considered in the outer loop right now
			for m,am in act:
				d_a = (an * am) **2
				if d_a > self.strenThr:				## if above strengthening threshold
					self.changeWeight(n,m,d_a)
						


	####################################################
	## output and visualization
	####################################################
	def __repr__(self):
		s = "ActivationNetwork\n-----------------------------\n"
		ids = self.nodes.keys()
		ids.sort()
		print(ids)
		for id in ids:
			n = self.nodes[id]
			a = self.act[n]
			s = s + "%8s/%1.5f -->> " % (n,a) + repr(self.succwei[n]) + "\n"
		return s[:-1]
			
		
		
	def vizualize(self,filename,makePNG=True,makePS=False):
		out = open(filename+".dot",'w')

		## options for graph output
		out.write("graph G {\n")
		#out.write("\tscale=false;")
		out.write("\toverlap=scale;\n")
		#out.write("\toverlap=true;\n")
		#out.write("\tsplines=true;\n")

		for n,a in self.act.iteritems():
			out.write('\t%s [label="%s/%0.3f"];\n' % (n,n,a))
			for m,w in self.succwei[n].iteritems():
				out.write('\t\t%s -- %s [label="%0.3f"];\n' % (n,m,w))
				
		out.write("}\n")
		out.close()

		# if makePNG:	os.system ("neato -Tpng -Gcharset=latin1 %s -o %s.png" % (filename,filename))
		# if makePS:	os.system ("neato -Tps -Gcharset=latin1 %s -o %s.ps"  % (filename,filename))
		
		if makePNG:	
			#os.system ("neato -Tpng %s -o %s.png" % (filename,filename))
			os.system ("dot -Tpng %s.dot -o %s.png" % (filename,filename))



class ActNetXY(ActNet):
	RANDOM_LAYOUT = 1
	CIRCULAR_LAYOUT = 2
	SPIRAL_LAYOUT = 3
	def __init__(self, *args, **kwds):
		ActNet.__init__(self, *args, **kwds)
		self.xy = {}
		self.bounds = (0,0,1000,1000)
	
	def iterXY(self):
		return IterDict(self.sortedNodes,self.xy)
	
	def setNodeLayout(self,layout=RANDOM_LAYOUT):
		pass
	
	def setBounds(self,x1,y1,x2,y2):
		self.bounds = (x1,y1,x2,y2)
	
	def getBounds(self):
		return self.bounds
		
	
	def addNode(self,n,pos=None):
		ActNet.addNode(self,n)
		if pos != None:
			self.xy[n] = pos
		else:
			self.xy[n] = self.newPos()
			
	
	def addNodes(self, nlist, poslist):
		for n,pos in nlist:
			self.addNode(n,pos)

	def newPos(self):
		x1,y1,x2,y2 = self.bounds
		return (random.randrange(x1,x2),random.randrange(y1,y2))
		
	def setNodePos(self,n,pos):
		if not self.present(n):
			raise ValueError, ("Node %s not present." % n) 
		self.xy[n] = pos
		
	def getNodePos(self,n):
		return self.xy[n]
		
						
def demo():
	print("(A) make some Network, add 5 nodes and activate 'a' and 'b' ")
	an = ActivationNetwork()
	an.addNodes(['a','b','c','d','e'])
	an.setAct('a', 0.9)
	an.setAct('b', 0.4)
	print(an)
	
	print("Change the activation exceeding the boundary, negative and positive")
	an.changeActBound('b',.78)
	an.changeActBound('a',-.05)
	print(an)
	
	
	print("Set some weights: a-b, a-c, b-c")
	an.setWeight('a','b',0.7)
	an.setWeight('a','c',0.8)
	an.setWeight('b','c',0.8)
	an.setWeight('e','c',0.2)
	print(an)
	
	
	print("Change some weights: a-c")
	an.setWeight('a','c',0.6)
	an.setWeight('a','c',0.6)
	an.setWeight('b','c',0.01)
	an.setWeight('d','c',0.01)
	an.deleteConn('c','e')
	print(an)
	
def demo2():
	from WozualizeB import Viz
	
	print("make some Network, add 5 nodes and activate 'a' and 'b' and 'c' ")
	an = ActivationNetwork()
	an.addNodes(['a','b','c','d','e'])
	an.setAct('a', 0.9)
	an.setAct('b', 0.4)
	#an.setAct('c', 0.8)
	#an.setAct('e', 0.5)
	#print("Set some weights: a-b, e-c")
	#an.setWeight('a','b',0.7)
	an.setWeight('e','c',0.2)
	print(an)
	
	an.vizualize("g1",makePNG=True)
	
	an.strenSimultAct()
	print(an)
	an.vizualize("g2",makePNG=True)
	viz = Viz()
	viz.showPic("g1.png")
	viz.showPic("g2.png")
	viz.show()
	
def demo3():
	import re
	import WTextServicesB

	text4 = """right at beginning of project right in earliest conceptu stag we orientation building giv exampl we re 
	working som museum at moment whol journey through museum absolut fundam design of museum"""

	text = text4
	text = text.lower()
	r = re.compile(ur'[\W\n\r]+')
	seq = r.split(text)
	print (seq)

	words = WTextServicesB.Counter()
	print (words)

	for i in seq:
		if i != '':
			words.input(i)

	an = ActivationNetwork()
	an.addNodes(words.objectsSorted())
	#print (an)
	#an.vizualize("xxx",makePNG=True)

	for i,k in enumerate(seq):
		print("processing %s..%s" % (i,k))
		an.maximizeAct(k)
		an.strenSimultAct()
		print(an)
		an.vizualize("%08d"%i,makePNG=True)
		an.decay()
		
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
	
	
#demo3()


			#verheiz = act.copy()		# verheiz contains all sufficiently activated nodes m_i for which  
										# the connection n->m_i has not been considered so far.
			#del verheiz[n]		# n->n has not to be considered.
			
			#nwei = []
			
			### first, modify the weights of all existing connections n->m  
			# #for m,w in self.succwei[n].iteritems():
			# #	d_a = (an * self.act[m]) **2		
			# #	if d_a > self.strenThr:				## if above strengthening threshold
			# #		self.succwei[n][m] = w + d_a		## append increased weight to new weights list
			# #	# #else:
			# #	# #	nwei.append(w)				## otherwise just the original weight
			# #	
			# #	## remove the successor node from the verheiz-dictionary -- to show that it has been handled already
			# #	del verheiz[m] 
			# #
			# #self.succwei[n] = nwei
			# ### nun den rest, der genau die in verheiz verbliebenen knoten, fuer die neue verbindungen her muessen
			# ### second, append new connections between simultaneously activated nodes whicht have not been considered before
			# #for m, am in verheiz.iteritems():
			# #	d_a = (an * am) **2
			# #	if d_a > self.strenThr and self.ids[n] < self.ids[m]:				## if above strengthening threshold
			# #		self.succwei[n][m].append(d_a)		## append increased weight to new weights list
			# #		self.succ[n].append(m)			## no else part here, we only have to append new connections but not to transfer old ones

		# #### same again for the predecessors
		# #for n,an in act.iteritems():
		# #	verheiz = act.copy()		# verheiz contains all sufficiently activated nodes m_i with 
		# #								# connection m_i->n has not been considered so far.
		# #	
		# #	del verheiz[n]				# n->n has not to be considered.
		# #	
		# #	nwei = [] 
		# #	for m,w in zip(self.pred[n],self.predwei[n]):
		# #		if m in act:
		# #			d_a = (an * act[m]) **2
		# #			if d_a > self.strenThr:			## if above strengthening threshold
		# #				nwei.append(w + d_a)		## append increased weight to new weights list
		# #			else:
		# #				nwei.append(w)				## otherwise just the original weight
		# #			## remove the successor node from the verheiz-dictionary
		# #			del verheiz[m] 
		# #	
		# #	self.predwei[n] = nwei
		# #	## nun den rest, der genau die in verheiz verbliebenen knoten, fuer die neue verbindungen her muessen
		# #	## append remaining to the successor lists of n
		# #	for m, am in verheiz.iteritems():
		# #		d_a = (an * am) **2
		# #		if d_a > self.strenThr and self.ids[n] > self.ids[m]:				## if above strengthening threshold
		# #			self.predwei[n].append(d_a)		## append increased weight to new weights list
		# #			self.pred[n].append(m)			## no else part here, we only have to append new connections but not to transfer old ones

