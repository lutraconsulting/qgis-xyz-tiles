import re
import unicodedata
from xml.sax.saxutils import escape
from qgis.core import (QgsProject, QgsCoordinateTransform)

import random
import string

class UTILS:

    """
    Use safer names.
    """
    @staticmethod
    def normalizeName(name, isFilename=True, escapeXml=True, removeAccents=True):
        normalized = name
        if escapeXml:
            normalized = UTILS.escapeXml(normalized)
        if removeAccents:
            normalized = UTILS.strip_accents(normalized)
        if isFilename:
            normalized = UTILS.escapeFilename(normalized)
        return normalized.lower()

    @staticmethod
    def escapeFilename(content):
        return re.sub(r"\W", "_", content)

    #https://pynative.com/python-generate-random-string/
    @staticmethod
    def randomString(stringLength=27):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    #Return the map extents in the given projection
    @staticmethod
    def getMapExtent(layer, projection):
        mapExtent = layer.extent()
        src_to_proj = QgsCoordinateTransform(layer.crs(), projection, QgsProject.instance().transformContext() if getattr(layer, "transformContext", None) is None else layer.transformContext())
        return src_to_proj.transformBoundingBox(mapExtent)

    @staticmethod
    def escapeXml(content):
        return escape(content)

    @staticmethod
    def strip_accents(s):
       return ''.join(c for c in unicodedata.normalize('NFD', s)
                      if unicodedata.category(c) != 'Mn')
