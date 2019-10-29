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

class NotFoundError(Exception):
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
        elementXpath = ".//svg:g[@id='%s']" % id
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
                                    ExistingDoc._NS):
            id = el.get('id')
            if id in ids:
                if id in result:
                    raise ParseError("Duplicate element with id %s" % id)
                result[id] = el
        return result

    def getSVGElement(self, tag, id):
        """ `tag` is the local svg tagname, without any
            namespace prefixes (e.g. 'rect', 'g')"""
        elementXpath = ".//svg:%s[@id='%s']" % (tag,id)
        r = self.root.find(elementXpath, ExistingDoc._NS)
        return r

    def save(self, file):
        self.tree.write(file, encoding="utf8")

class SVGDocInScale(ExistingDoc):
    """ Inject graphical content into an existing SVG document
        based on multiple target areas / injection points
        in the document.
        """

    def getLayerInjector(self, id, hrange, vrange, group=None, **deltaFnHV):
        """ Get a `ScaledInjectionPoint` instance for injecting
            content into the layer top-level element.

            Transformation parameters will be based on the
            document top-level element's viewBox and the given
            visible ranges `hrange` and `vrange` in world
            coordinates.

            `_deltaFnHV` can be used to define custom delta
            calculation methods (cf. `NumDocTrafo`)."""
        target_el = self.getLayer(id)
        if not target_el:
            raise NotFoundError("No Layer with id=%s" % id)
        ### if group element is given, insert it as inj. target
        if group is not None:
            g = ET.fromstring(group)
            target_el.append(g)
            target_el = g
        return ScaledInjectionPoint(target_el,
                                    self.viewBox(),
                                    hrange, vrange,
                                    **deltaFnHV)

    def getRectInjector(self, id, hrange, vrange, **deltaFnHV):
        target_el = self.getSVGElement('rect', id)
        if target_el is None:
            raise NotFoundError("No `rect` element with id=%s" % id)

        ### derive target area from the rect geometry
        viewBox = list(map(float, (target_el.attrib['x'],
                                   target_el.attrib['y'],
                                   target_el.attrib['width'],
                                   target_el.attrib['height'])))
        ### copy the original injection rect
        cpy_el = ET.fromstring(ET.tostring(target_el))
        ### replace a `rect` by a `g` in the exact same position
        # for a first cut: the hacky way:
        # avoid fiddeling with parents and idices
        # FIXME: Maybe, these attribs should not be written?
        target_el.tag = target_el.tag.replace('rect','g')
        target_el.attrib = {'id': "INJ_%s" % id}
        ### make the copy translucent and add it to the target
        cpy_el.attrib['opacity'] = "0.452"
        target_el.append(cpy_el)
        ### create and return the injection point
        return ScaledInjectionPoint(target_el,
                                    viewBox,
                                    hrange, vrange,
                                    **deltaFnHV)

class NumDocTrafo(object):
    """ Transform numbers `h` and `v` (horizontal and
        vertical positions in some 'world' coordinate system)
        into document coordinates `x` and `y`. Horizontal and
        vertical world coordinates can have different (physical)
        units. `__init__` dynamically creates the tranformation
        functions `h2x` and `v2y` as instance properties
        (not methods!).

        For cases where the built-in operator `-` is not
        suitable for calculating deltas between world
        coordinates, alternative delta functions can be defined
        for one or both dimensions. The default unit of the
        document is assumed to be pixels. The world coordinates
        have to be numbers without unit."""
    def __init__(self, viewBox, hrange, vrange,
                 deltaFnH=None, deltaFnV=None):
        """ Initialize document and world coordinate systems,
            including the transformation functions, as
            dynamically generated instance properties (not
            methods!).

            `viewBox` is of the SVG canonical form
            (x,y,width,height) where x, y, width, and height are
            numbers, not strings.

            If `deltaFnH` and/or `deltaFnV` are specified
            they override the canonical difference operation
            `-` for horizontal/vertical world coordinates.
            This can be useful for non-trivial
            numeric representations such as python's `datetime`
            and `timedelta`, which needs conversion into
            number of seconds for further calculations."""
        ### Define the View on the data: horizontal, vertical
        self.h1, self.h2 = hrange
        self.v1, self.v2 = vrange
        ### document dimensions: x, y
        self.x1, self.y1, width, height = viewBox
        ### init scale factors and transformation functions
        if deltaFnH is not None:
            # use non-trivial delta calculation function
            self.HXscale = width / deltaFnH(self.h1, self.h2)
            self.h2x = lambda h,                \
                              h1=self.h1,       \
                              x1=self.x1,       \
                              sc=self.HXscale,  \
                              D=deltaFnH : D(h1,h)*sc + x1
        else:
            # simple and fast via built-in `-`
            self.HXscale = width / (self.h2-self.h1)
            self.h2x = lambda h,           \
                              h1=self.h1,  \
                              x1=self.x1,  \
                              sc=self.HXscale : (h-h1)*sc + x1

        if deltaFnV is not None:
            # use non-trivial delta calculation function
            self.VYscale = heigth / deltaFnV(self.v1, self.v2)
            self.v2y = lambda v,                \
                              v1=self.v1,       \
                              y1=self.y1,       \
                              sc=self.VYscale,  \
                              D=deltaFnV : D(v1,v)*sc + y1
        else:
            # simple and fast via built-in `-`
            self.VYscale = height / (self.v2-self.v1)
            self.v2y = lambda v,           \
                              v1=self.v1,  \
                              y1=self.y1,  \
                              sc=self.VYscale : (v-v1)*sc + y1

    def h2x(num):
        """ Transform world numbers `num` to horizontal
            document x-coordinates. This stub will be replaced
            by __init__."""
        raise Exception("Internal error: h2x was not initialized properly. Please contact the administrator ,-)")

    def v2y(num):
        """ Transform world numbers `num` to vertical
            document y-coordinates. This stub will be replaced
            by __init__."""
        raise Exception("Internal error: h2x was not initialized properly. Please contact the administrator ,-)")

class ScaledInjectionPoint(NumDocTrafo):
    """ Represents a target element in a parsed SVG (XML)
        document for the purpose of injecting SVG content.

        Each ScaledInjectionPoint comes with its own rectangular
        target area in the document, usually derived from a
        `rect` element or a `viewBox` attribute. A pair of
        'visible' ranges defines the 'view' on the data in a
        world/source/data/user-chosen coordinate system."""
    def __init__(self, target_element, viewBox, hrange, vrange,
                 **deltaFnHV):
        super().__init__(viewBox, hrange, vrange, **deltaFnHV)
        self.target = target_element

    def inject(self, content):
        if isinstance(content, ET.Element):
            self.target.append(inj)
        else:
            try:
                self.target.append(ET.fromstring(content))
            except (ET.ParseError, TypeError) as e:
                raise ParseError("Invalid type or syntax for content %s" % content)
