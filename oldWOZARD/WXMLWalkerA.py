from xml.dom.minidom import parse
from sys import argv


class XMLDocument(object):
	def __init__(self,filename):
		dom = parse(filename)
		self.dom = dom		

	def __iter__(self):
		return XMLDepthWalker(self.dom)


class XMLDepthWalker(object):
	def __init__(self,dom):
		self.nextNode = dom
		self.level = 0
		
	def next(self):
		if (self.nextNode == None) or (self.level < 0):
			raise StopIteration
			
		thisNode = self.nextNode
		thisLevel = self.level
		
		if thisNode.firstChild != None:
			## jump down deeper into the tree
			self.nextNode = thisNode.firstChild
			self.level += 1
		elif thisNode.nextSibling != None:
			## go on on the same level
			self.nextNode = thisNode.nextSibling
		else:
			## going up and right (to the next sibling of the parent)
			self.nextNode = thisNode.parentNode.nextSibling
			self.level -= 1
		return thisLevel,thisNode
		
	def __iter__(self):
		return self
		
#class XMLDepthWalkerFiltered(XMLWalker)
	
