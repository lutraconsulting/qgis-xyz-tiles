import re

import math
import os
import unicodedata
from xml.sax.saxutils import escape
from qgis.core import (QgsProject, QgsCoordinateTransform, QgsMessageLog)

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
        projection.validate()
        layer.crs().validate()
        src_to_proj = QgsCoordinateTransform(layer.crs(), projection, QgsProject.instance().transformContext() if getattr(layer, "transformContext", None) is None else layer.transformContext())
        return src_to_proj.transformBoundingBox(mapExtent)

    @staticmethod
    def escapeXml(content):
        return escape(content)

    @staticmethod
    def strip_accents(s):
       return ''.join(c for c in unicodedata.normalize('NFD', s)
                      if unicodedata.category(c) != 'Mn')

    # TMS functions taken from https://alastaira.wordpress.com/2011/07/06/converting-tms-tile-coordinates-to-googlebingosm-tile-coordinates/ #spellok
    @staticmethod
    def tms(ytile, zoom):
        n = 2.0 ** zoom
        ytile = n - ytile - 1
        return int(ytile)

    # Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
    @staticmethod
    def deg2num(lat_deg, lon_deg, zoom):
        QgsMessageLog.logMessage(" e ".join([str(lat_deg), str(lon_deg), str(zoom)]), tag="Processing")
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    # Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
    @staticmethod
    def num2deg(xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/12611523
    @staticmethod
    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None
