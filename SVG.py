"""Get infos from and inject elements into existing SVG files."""

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
        """ Get viewBox of the toplevel SVG element (root).
            returns a sequence of the form `[x,y,width,height]`."""
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

class BaseNumDocTrafo(object):
    """ BaseNumDocTrafo is an abstract class. Please
        override __init__.

        Transform numbers `h` and `v` defining
        horizontal and vertical positions in some
        'world' coordinate system into
        document coordinates `x` and `y`. The number
        is assumed to have a different scale (i.e.
        physical unit) when scaling to horizontal
        `h2x` compared to vertical `v2y` document
        positions.

        This is a base class, refraining from any
        assumptions about how the dimensions of the
        target view/box/area in the document are
        derived.
        The default unit of the document is assumed
        to be pixels; the world coordinates are
        numbers without unit."""
    def __init__(self):
        """ The scale factors `_HXscale`, `_VYscale` as
            well as the offsets of the view from the
            respective origins of the world and document
            coordinate systems `x1`, `y1`, `h1`,
            `v1` need to be defined by overriding
            `__init__`."""
        raise NotImplementedError("Please override __init__ to define the transformation parameters.")

    def h2x(self, num):
        """ Transform world numbers `num` to horizontal
            document x-coordinates."""
        delta = num - self.h1
        return delta*self._HXscale + self.x1

    def v2y(self, num):
        """ Transform world numbers `num` to vertical
            document y-coordinates."""
        delta = num - self.v1
        return delta*self._VYscale + self.y1

class BaseNumDocTrafo_DeltaFn(BaseNumDocTrafo):
    """ Like `BaseNumDocTrafo` but less efficient. In addition
        a function can be defined for calculating the delta
        between two values `v1`, `v2` and/or `h1`, `h2`."""
    def __init__(self, deltaFnH=(lambda h1,h2:h2-h1),
                       deltaFnV=(lambda v1,v2:v2-v1)):
        self.deltaFnH = deltaFnH
        self.deltaFnV = deltaFnV

    def h2x(self, num):
        delta = self.deltaFnH(self.h1, num)
        return delta*self._HXscale + self.x1

    def v2y(self, num):
        delta = self.deltaFnV(self.v1, num)
        return delta*self._VYscale + self.y1
