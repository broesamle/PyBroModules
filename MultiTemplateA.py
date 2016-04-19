""" 
Conditional or sequential combination of pythons standard Templating mechanism.
Several instances of string.Template are combined. The resulting TemplateCollection
object has the same API as string.Template. Based on the keys/values 
in the dictionary passed to the substitute operation, TemplateCollection will
determine which string.Template instance(s) will be used. For this purpose, a detector function
is attached to each elmentary Template in the TemplateCollection.

I know there is more syntactic and not so extremely OOPish templating engines, 
but I got used to this technique, for quite some time now : )
"""

from string import Template
import copy

class TemplateCollection(object):
	def __init__(self,templatestringsNdetectorfunctions = [],wrapper="$THESERIES"):
		""" templatestringsNdetectorfunctions is of the form (str,fn),
			fn testing the dictionary for presence or absence of a certain feature and str being the template corresponding 
			to that feature. If the feature is found ie fn(dict) returns true dict will be applied to the corresponding template string str."""
		self.temNdet = copy.copy(templatestringsNdetectorfunctions)
		self.wrapper = Template(wrapper)
		
	def addTemplate(self,templateStr,detectorFn):
		self.temNdet.append((Template(copy.deepcopy(templateStr)),detectorFn))

	def substitute(self,dict,**kwargs):
		"""please overload!"""
		pass

	def safe_substitute(self,dict,**kwargs):
		"""please overload!"""
		pass

class TemplateSeries(TemplateCollection):
	def __init__(self,*args,**kwargs):
		TemplateCollection.__init__(self,*args,**kwargs)

	def substitute(self,dict,**kwargs):
		result = ""
		for tem,det in self.temNdet:
			if det(dict):
				result += tem.substitute(dict,**kwargs)
		
		return self.wrapper.substitute(dict,THESERIES=result)
	
	def safe_substitute(self,dict,**kwargs):
		result = ""
		for tem,det in self.temNdet:
			if det(dict):
				result += tem.safe_substitute(dict,**kwargs)
		return self.wrapper.safe_substitute(dict, THESERIES=result)

class TemplateChoice(TemplateCollection):
	def __init__(self,*args,**kwargs):
		TemplateCollection.__init__(self,*args,**kwargs)

	def substitute(self,dict,**kwargs):
		for tem,det in self.temNdet:
			if det(dict):
				return tem.substitute(dict,**kwargs)

	def safe_substitute(self,dict,**kwargs):
		for tem,det in self.temNdet:
			if det(dict):
				return tem.safe_substitute(dict,**kwargs)
