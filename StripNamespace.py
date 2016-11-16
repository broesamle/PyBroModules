import io
import xml.etree.ElementTree as ET

### Source: http://stackoverflow.com/questions/8113296/supressing-namespace-prefixes-in-elementtree-1-2
### (I am not the only one to copy this snippet:
### https://github.com/Remi-C/PPPP_utilities/blob/master/pointcloud/test_reading_ply_with_python.py)

### Every now and then I am even more greatful that it still works
### : )

class StripNamespace(ET.TreeBuilder):
    """ Remove Namespace prefixes from the tags.
        Source: http://stackoverflow.com/questions/8113296/supressing-namespace-prefixes-in-elementtree-1-2
        """
    def start(self, tag, attrib):
        tag = stripNamespaceFromTag(tag)
        super(StripNamespace, self).start(tag, attrib)
    def end(self, tag):
        tag = stripNamespaceFromTag(tag)
        super(StripNamespace, self).end(tag)

def stripNamespace(content):
    target = StripNamespace()
    parser = ET.XMLParser(target=target)
    root = ET.XML(content, parser=parser)
    s = io.StringIO()
    ET.ElementTree(root).write(s,encoding='unicode')
    return s.getvalue()

def stripNamespaceFromTag(tag):
    index = tag.find('}')
    if index != -1:     return tag[index+1:]
    else:               return tag
