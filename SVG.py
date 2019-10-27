""" Inject SVG content into existing SVG files.
    Technically, parsing and manipulating documents, elements,
    trees, sub-trees relies on python's `xml.etree.ElementTree`,
    (ElementTree or ET in this document).
    """

import re
import xml.etree.ElementTree as ET

### This affects all modules also using ET :(
ET.register_namespace('',"http://www.w3.org/2000/svg")
ET.register_namespace('xlink',"http://www.w3.org/1999/xlink")

class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ExistingDoc(object):
    """ Open existing SVG documents for retrieving content or
        information as well as for injecting new SVG content.
        New content can be provided as `ElementTree.Element`
        or SVG string."""
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
        """ Retrieve all `<g id="ID">` elements for a set of
            given `ids` and return them as dict of
            `ElementTree.Element` instances. For instance,
            layers in vector graphics applications often follow
            this pattern.
            The returned dictionary maps each ID to
            its toplevel element; ID must be in `ids` and
            a suitable element must exist in the document."""
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

    def save(self, file):
        self.tree.write(file, encoding="utf8")

class SVGDocInScale(ExistingDoc):
    """ While there can be multiple plot/view areas with
        individual scaling and positioning in the document,
        the function for calculating differences (deltas)
        between world coordinates needs to be defined once
        for each ScaledSVGInjector instance."""

    def __init__(self, file, **deltaFnHV):
        """ `file` can be a file-like object or a filename.
            If `deltaFnH` and/or `deltaFnV` are specified
            they override the canonical difference operation
            `-` for horizontal/vertical world coordinates.
            This can be useful for non-trivial numeric
            representations such as pythons `datetime` and
            `timedelta`, which needs to be converted into
            number of seconds for further calculations."""
        self._deltaFnHV = deltaFnHV
        super().__init__(file)

    def getLayerInjector(self, id, hrange, vrange):
        ### Get the document dimensions
        return ScaledInjectionPoint(self.getLayer(id),
                                    self.viewBox(),
                                    hrange, vrange,
                                    **self._deltaFnHV)

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

### FIXME: Currently, the implementation is based on
#   BaseNumDocTrafo_DeltaFn.
#   Dynamic re-plugging of methods via meta-programming
#   could achieve a flexible runtime choice between
#   the fast built-in and the parameterised
#   `BaseNumDocTrafo_DeltaFn` approach of difference
#   calculation.
class ScaledInjectionPoint(BaseNumDocTrafo_DeltaFn):
    """ Represents a target element in a parsed SVG (XML) document
        for later injection of SVG/XML content.
        In addition to the SVG document handling it also
        provides the scaling functionality for world coords
        into document coords based on a specific world view
        and document targed area.
        """
    def __init__(self, target_element, viewBox, hrange, vrange,
                 **deltaFnHV):
        super().__init__(**deltaFnHV)
        self.target = target_element

        ### Define the View on the data: horizontal, vertical
        self.h1, self.h2 = hrange
        self.v1, self.v2 = vrange

        ### document dimensions: x, y
        # self.x2, self.y2 = self._x1+wdoc,self._y1+hdoc
        self.x1, self.y1, width, height = viewBox

        ### scale factors for transforming world to doc coords
        self._HXscale = width / self.deltaFnH(self.h1, self.h2)
        self._VYscale = height / self.deltaFnV(self.v1, self.v2)

    def inject(self, content):
        if isinstance(content, ET.Element):
            self.target.append(inj)
        else:
            try:
                self.target.append(ET.fromstring(content))
            except (ET.ParseError, TypeError) as e:
                raise ParseError("Invalid type or syntax for content %s" % content)
