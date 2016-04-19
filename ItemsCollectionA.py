"""
Read collections of items (files etc.) into an OrderedDict.
Each item is identified using a unique key. It can have any number of attribute/value pairs.
The key is defined for all items, for other attributes there may (but does not have to) be an overlap across items.
The module defines
"""

from collections import OrderedDict
from string import Template
import os, fnmatch, codecs

class ItemsCollection(OrderedDict):
	""" Collects Items in an OrderedDict. Each Item is, in turn, a dictionary.
		Overall, a collection of attribute/value items. This structure is
		useful for later using the dictionary in a templating mechanism."""
	def __init__(self,defaults={}):
		OrderedDict.__init__(self)
		self.defaults = defaults

	def addItem(self,key,dict):
		""" Add a dict as an item to the ItemsCollection, using key,"""
		if key in self: raise ValueError("Rubrique exists: %s" % key)
		#print ("addItem", key)
		self[key] = dict
		self[key]['THIS_ELEMENT_KEY'] = key

		for k,v in self.defaults.items():
			if k not in self[key]:	self[key][k] = v

	def tryReformatFields(self,fields,mapping):
		""" In some cases it is useful to do a (failsafe) post process a number of fields."""
		for k in self.keys():
			for f in fields:
				try: self[k][f] = mapping(self[k][f])
				except Exception:
					pass

#	def generateItem(self,key,template,**kwargs):
#		return Template(template).safe_substitute(self[key],**kwargs)

	def generateSeries(self,itemTEM=Template("ENTRYDUMMY"),seriesTEM=Template("$THEITEMS"),itemData={},seriesData={},filterFn=lambda itemdict:True,counterFn=lambda i:str(i), separator=""):
		itemsHTML = ""

		sep = ""
		for i,(key,dict) in enumerate(self.items()):
			if filterFn(dict):
				itemHTML = itemTEM.safe_substitute(dict,ITEMCOUNTER=counterFn(i),**itemData)
				itemsHTML += sep+itemHTML
			sep = separator
		try:
			result = seriesTEM.substitute(THEITEMS=itemsHTML,**seriesData)
		except KeyError as ke:
			result = seriesTEM.safe_substitute(THEITEMS=itemsHTML,**seriesData)
		return result

class FilesCollection(ItemsCollection):
	""" Use a number of files to define the collection of items."""
	def __init__(self,inputDIR=".",pattern="*.mdtxt",filesList=None,reverse=False,**kwargs):
		self.inPath = inputDIR
		ItemsCollection.__init__(self,**kwargs)
		if not filesList:
			filesList = os.listdir(inputDIR)
		else:
			pattern = "*"
		
		filesList.sort(reverse=reverse)
		for file in filesList:
			if fnmatch.fnmatch(file,pattern):
				filename= os.path.join(inputDIR,file)
				self.processFile(self.keyFromFilename(file),inputDIR,file)

	def keyFromFilename(self,file):
		"""Please override this method! By default this returns the filename without extension."""
		return os.path.splitext(file)[0]

	def processFile(self,key,filepath,filename):
		"""Please override this method! It is a hook for code to process each file correctly."""
		pass

class FilesInputCollection(FilesCollection):
	""" Use a number of files to define the collection of items and process the content of the file."""
	def __init__(self,*args,**kwargs):
		FilesCollection.__init__(self,*args,**kwargs)

	def processFile(self,key,filepath,filename):
		input_file = codecs.open(os.path.join(filepath,filename), mode="r", encoding="utf-8")
		text = input_file.read()
		input_file.close()
		self.processInput(key,text)

	def processInput(self,key=None,text=""):
		"""Please override this method! It is a hook for processing the text from the each processed file."""
		pass