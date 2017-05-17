"""
Read collections of items (files etc.) into an OrderedDict.
Each item is identified using a unique key. It can have any number of attribute/value pairs.
The key is defined for all items, for other attributes there may (but does not have to) be an overlap across items.
The module defines
"""

from collections import OrderedDict
from string import Template
import os, fnmatch, codecs

try:
    import markdown
except ImportError:
    print ('[ItemsCollectionA] module markdown was not loaded!')

class ItemsCollection(OrderedDict):
    """ Collects Items in an OrderedDict. Each Item is, in turn, a dictionary.
        Overall, a collection of attribute/value items. This structure is
        useful for later using the dictionary in a templating mechanism."""
    def __init__(self,defaults={},strictsubstitute=False):
        """
        `defaults` defines which fields to add when absent in a new item dictionary.
        If `strictsubstitute == True`, missing fields will cause error during substitution.
        """
        OrderedDict.__init__(self)
        self.defaults = defaults
        self.strictsubstitute = strictsubstitute

    def addItem(self,key,dict):
        """ Add a dict as an item to the ItemsCollection, using key,"""
        if key in self: raise ValueError("Rubrique exists: %s" % key)
        #print ("addItem", key)
        self[key] = dict
        self[key]['THIS_ELEMENT_KEY'] = key

        for k,v in self.defaults.items():
            if k not in self[key]:  self[key][k] = v

    def tryReformatFields(self,fields,mapping):
        """ In some cases it is useful to do a (failsafe) post process a number of fields."""
        for k in self.keys():
            for f in fields:
                try: self[k][f] = mapping(self[k][f])
                except Exception:
                    pass

    def generateSeries(self,itemTEM=Template("ENTRYDUMMY"),seriesTEM=Template("$THEITEMS"),itemData={},seriesData={},filterFn=lambda itemdict:True,counterFn=lambda i:str(i), separator=""):
        itemsHTML = ""

        sep = ""
        for i,(key,dict) in enumerate(self.items()):
            if filterFn(dict):
                if self.strictsubstitute:
                    try:
                        itemHTML = itemTEM.substitute(dict,ITEMCOUNTER=counterFn(i),**itemData)
                    except KeyError as ke:
                        raise KeyError("Undefined field in item substitute: %s" % ke)
                else:
                    itemHTML = itemTEM.safe_substitute(dict,ITEMCOUNTER=counterFn(i),**itemData)
                itemsHTML += sep+itemHTML
            sep = separator
        if self.strictsubstitute:
            try:
                result = seriesTEM.substitute(THEITEMS=itemsHTML,**seriesData)
            except KeyError as ke:
                raise KeyError("Undefined field in overall series: %s" % ke)
        else:
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

class MDFilesCollection(FilesInputCollection):
    def __init__(self, *args, **kwargs):
        if not markdown:
            raise Error("Module markdown is required for MDFilesCollection.")
        self.md = markdown.Markdown(extensions = ['markdown.extensions.meta'])
        FilesCollection.__init__(self, *args, reverse=False, **kwargs)

    def processInput(self, key=None, text=""):
        html =  self.md.reset().convert(text)
        try:
            self.addItem(key, self.md.Meta)
        except Exception as e:
            print ("key of file with empty meta info (or the like):",key)
            raise e

        self[key]['contentHTML'] = html.strip()

    DEFAULTTEMPLATE = Template("""TEMPLATE FOR $THIS_ELEMENT_KEY:
        $contentHTML
        $PREV_LINK
        $NEXT_LINK
        """)
    def iterateSeries(self,
                      template=DEFAULTTEMPLATE,
                      prevlinktemplate=Template("PREVLINK: $ELEMENT_KEY"),
                      nextlinktemplate=Template("NEXTLINK: $ELEMENT_KEY"),
                      prevlink_forfirst="",
                      nextlink_forlast="",
                      additionalfields={}):

        return LinkedSeriesIterator(self, template,
                                    prevlinktemplate, nextlinktemplate,
                                    prevlink_forfirst, nextlink_forlast,
                                    additionalfields)

class LinkedSeriesIterator(object):
    def __init__(self,
                 collection,
                 template,
                 prevlinktemplate,
                 nextlinktemplate,
                 prevlink_forfirst,
                 nextlink_forlast,
                 additionalfields):
        self.template = template
        self.collectionitems = collection.items().__iter__()
        self.prevlinktemplate = prevlinktemplate
        self.nextlinktemplate = nextlinktemplate
        self.prevlink_forfirst = prevlink_forfirst
        self.nextlink_forlast = nextlink_forlast
        self.additionalfields = additionalfields
        self.thiskey, self.thisvalue = "", None
        self.prevkey, self.prevvalue = "", None
        try:
            self.nextkey, self.nextvalue = self.collectionitems.__next__()
        except StopIteration:
            self.nextkey, nextvalue = "", None

    def __iter__(self):
        return self

    def __next__(self):
        self.prevkey, self.prevvalue = self.thiskey, self.thisvalue
        self.thiskey, self.thisvalue = self.nextkey, self.nextvalue
        if not self.thiskey: raise StopIteration
        try:
            self.nextkey, self.nextvalue = self.collectionitems.__next__()
        except StopIteration:
            self.nextkey, self.nextvalue = "", None

        if self.prevkey:
            prev_link = self.prevlinktemplate.substitute(self.prevvalue,
                                                         ELEMENT_KEY=self.prevkey)
        else:
            prev_link = self.prevlink_forfirst

        if self.nextkey:
            next_link = self.nextlinktemplate.substitute(self.nextvalue,
                                                         ELEMENT_KEY=self.nextkey)
        else:
            next_link = self.nextlink_forlast

        return self.thiskey, self.template.substitute(
            self.thisvalue,
            PREV_ELEMENT_KEY=self.prevkey,
            THIS_ELEMENT_KEY=self.thiskey,
            NEXT_ELEMENT_KEY=self.nextkey,
            PREV_LINK=prev_link,
            NEXT_LINK=next_link,
            **self.additionalfields)
