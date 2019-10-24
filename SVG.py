import re
import xml.etree.ElementTree as ET

### This affects all modules also using ET :(
ET.register_namespace('',"http://www.w3.org/2000/svg")
ET.register_namespace('xlink',"http://www.w3.org/1999/xlink")

class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ExistingDoc(object):
    """ Open existing SVG documents for
        retrieving content or information."""
    _NS = {'svg' :'http://www.w3.org/2000/svg'}
    def __init__(self, filename):
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()

    def viewBox(self):
        vbox = self.root.get('viewBox', None)
        if isinstance(vbox, str):
            coords = re.findall("([^\s,]+)+", vbox)
            if len(coords) != 4:
                raise ParseError("viewBox coordinates not valid: %s" % vbox)
            return list(map(float, coords))
        elif vbox == None:
            return None
        else:
            raise ParseError("Unknown error while parsing viewBox coordinates: %s" % vbox)

    def getLayer(self, id):
        elementXpath = "svg:g[@id='%s']" % id
        return self.root.find(elementXpath, ExistingDoc._NS)

    def getLayersByID_dict(self, ids):
        """ Retrieve all `<g id="ID">` elements `e`
            for a set of given `ids` as dict of
            `xml.etree.ElementTree.Element` instances.
            I.e., AI layers fall into this pattern.
            The returned dictionary `r` contains
            elements `e` so that `r['ID'] = e` for
            each element which has an `ID` in `ids`
            and exists in the document."""
        elementXpath = "svg:g[@id]"
        result = {}
        for el in self.root.findall(elementXpath,
                                    _NS):
            id = el.get('id')
            if id in ids:
                if id in result:
                    raise ParseError("Duplicate element with id %s" % id)
                result[id] = el
        return result

class Injector(ExistingDoc):
    """ Open existing SVG documents for injecting
        new SVG content. New content can be provided
        as `xml.etree.ElementTree` or SVG string."""
    def inject(self, target, content):
        if isinstance(content, ET.Element):
            target.append(inj)
        else:
            try:
                target.append(ET.fromstring(content))
            except (ET.ParseError, TypeError) as e:
                raise ParseError("Invalid type or syntax for injcontent %s" % content)

    def save(self, file):
        self.tree.write(file, encoding="utf8")
