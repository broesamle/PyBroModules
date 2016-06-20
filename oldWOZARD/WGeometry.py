import pyx	
from WRender import PyXMultipageRenderer
import os, sys, collections
import numpy as np
#import logging
#from pyx.unit import x_mm,x_pt,w_mm,u_mm,v_mm
import random

from WContainer import PartitionedContainer,StochasticInteractionContainer,ContainerPrinter	

class ContainerRenderer(PyXMultipageRenderer):
	def __init__(self,*args,**kwargs):
		PyXMultipageRenderer.__init__(self, *args, **kwargs)
		self.partitionStyles = collections.OrderedDict()
		
		#if 'reaktor' in kwargs:
		#	rea = kwargs['reaktor']
		#	
		#	logging.info("Reaktor: SPAC:%f  DIAM:%f  DCAY:%f  FISS:%f" % (rea.spaceFactor,rea.diameter,rea.decayRate,rea.fissionRate))
		# logging.info(" fissile,  inDecay,   inFiss,     Rays, absorbed, unabsorb" )
		
	def addPartitionStyle(self,pa,style):
		if not self.simulate:
			self.partitionStyles[pa] = style

	def render(self,container):
		if not self.simulate:
			for pa,sty in self.partitionStyles.iteritems():
				for el in container.retrieve(pa):
					self.can.stroke(el,sty)
		#logging.info("%8d, %8d, %8d, %8d, %8d, %8d" % (len(rea.fissileAtoms), len(rea.inDecay), len(rea.inFission), len(rea.raysInfinity), len(rea.raysAbsorbed), len(rea.raysUnabsorbed)))

	
		
class GeometrieReaktorB(StochasticInteractionContainer):
	infinity = pyx.path.circle(0,0,100)

	@staticmethod
	def generateRay(el):
		x1,y1 = GeometrieReaktorB.getRndPoint(el)
		x2,y2 = GeometrieReaktorB.getInfinityPoint()
		results = [[pyx.path.line(x1,y1,x2,y2)]]	## why a list of one list with one element?
													## one element in one product channel -- other generators might want to generate two types of objects for different partitions/channels -- and maybe more than one object per channel
		return results

	@staticmethod
	def getInfinityPoint():
		return GeometrieReaktorB.getRndPoint(GeometrieReaktorB.infinity)
		
	@staticmethod
	def interactRayFissile(atom,ray):
		""" Interaction between one ray and a fissile atom. If an interaction is possible, products are
			send to the channels ['newcastRAYS','absRAYS','inFISS']."""
			
		isects = atom.intersect(ray)[0]
		if isects:
			param = random.sample(isects,1)[0]
			x0,y0 = ray.atbegin()
			x1,y1 = atom.at(param)
			x2,y2 = GeometrieReaktorB.getInfinityPoint()
			x3,y3 = GeometrieReaktorB.getInfinityPoint()
			products = [[pyx.path.line(x1,y1,x2,y2),pyx.path.line(x1,y1,x3,y3)],	# newly cast rays
						[pyx.path.line(x0,y0,x1,y1)]]								# absorbed ray
			return products
		else: 
			return []
		
	@staticmethod
	def getRndPoint(shape):
		return shape.at ( np.random.uniform ( 0, pyx.unit.tocm(shape.arclen()) ) )	

			
	def decay(self,rate=0.1):
		self.delete(partition='inDECAY')
		self.extract(srcPartition='FISSILE',destPartitions=['inDECAY'],move=True,rate=rate)
		self.generate(GeometrieReaktorB.generateRay,srcPartition='inDECAY',productChannels=[['castRAYS']])

	def fission(self,rate=1.0):
		self.delete(partition='inFISS')
		self.delete(partition='absRAYS')
		self.delete(partition='emmiRAYS')
		self.interact(interact=GeometrieReaktorB.interactRayFissile,
			srcPartition1='FISSILE',srcPartition2='castRAYS',
			destPartition1='inFISS',destPartition2='XXX',
			productChannels=[['newcastRAYS'],['absRAYS']],rate=rate)
		self.delete(partition='XXX')
		self.deletePartition('XXX')
		self.move(srcPartition='castRAYS',destPartitions=['emmiRAYS'])
		self.move(srcPartition='newcastRAYS',destPartitions=['castRAYS'])

	def addBlock(self,x1,y1,x2,y2,r,N,partition):
		X=list(np.random.uniform(x1,x2,N))
		Y=list(np.random.uniform(y1,y2,N))
		#print X
		#print Y
		collection = [pyx.path.circle(x,y,r) for x,y in zip(X,Y)]
		self.addElements(collection,["FISSILE",partition])
		
