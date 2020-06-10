import re
import time
import math
import os
import unicodedata
import tempfile
from http import HTTPStatus
from urllib.parse import urlencode
import requests
from xml.sax.saxutils import escape
from zipfile import ZipFile
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (QgsProject, QgsCoordinateTransform, QgsMessageLog, QgsVectorLayer, QgsRasterLayer)

import random
import string

class UTILS:

    #Danilo o zip precisa deletar dps
    @staticmethod
    def zipFiles(dir, pattern):
        curTmpFile = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        compPattern = re.compile(pattern)
        # create a ZipFile object
        with ZipFile(curTmpFile, 'w') as zipObj:
            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(dir):
                for filename in filenames:
                    if not compPattern.match(filename):
                        continue
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath, os.path.basename(filePath))
            return curTmpFile
        return None

    @staticmethod
    def getFileSize(dir, pattern):
        total = 0
        compPattern = re.compile(pattern)
        for folderName, subfolders, filenames in os.walk(dir):
            for filename in filenames:
                if not compPattern.match(filename):
                    continue
                filePath = os.path.join(folderName, filename)
                if os.path.isfile(filePath):
                    total = total + os.path.getsize(filePath)
        return total

    @staticmethod
    def checkForCanceled(feedback, msg='Cancelling'):
        if feedback.isCanceled():
            feedback.pushConsoleInfo(msg)
            raise Exception("User canceled the plugin execution.")

    #Danilo //Danilo return a  TemporaryFile when works
    #Danilo o zip precisa deletar
    @staticmethod
    def generateZipLayer(layer):
        print("Generating zip for " + layer.name() + " layer.")
        sourceUri = layer.dataProvider().dataSourceUri()
        absolutePath = None
        if isinstance(layer, QgsRasterLayer):
            if '.tiff' in sourceUri:
                absolutePath = sourceUri[:(sourceUri.index(".tiff") + 5)]
            elif '.tif' in sourceUri:
                absolutePath = sourceUri[:(sourceUri.index(".tif") + 4)]
            else:
                print("Only tiff and tif is allowable to download.")
        elif isinstance(layer, QgsVectorLayer):
            if '.shp' in sourceUri:
                absolutePath = sourceUri[:(sourceUri.index(".shp") + 4)]
            else:
                print("Only shp file is allowable to download.")
        if absolutePath is not None:
            fileName = os.path.basename(absolutePath)
            fileNameWithoutExt = os.path.splitext(fileName)[0]
            dirName = os.path.dirname(absolutePath)
            zipFile = UTILS.zipFiles(dirName + os.path.sep, fileNameWithoutExt + "*")
            zipFile.close()
            if os.path.getsize(zipFile.name) > 2e9:
                print("The map filesize is greater than the GitHub 2Gb limit. (all files in this folder starting with " + fileNameWithoutExt + " were included.")
            else:
                return zipFile
        return None


    @staticmethod
    def runLongTask(function, feedback, waitMessage="Please Wait", secondsReport=60, *args, **kwArgs):
        from concurrent import futures
        # feedback.setProgress(1)
        stepTimer = 0.5
        totalTime = 0
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            job = executor.submit(function, *args, **kwArgs)
            elapsedTime = 0
            while job.done() == False:
                time.sleep(stepTimer)
                elapsedTime = elapsedTime + stepTimer
                totalTime = totalTime + stepTimer
                if elapsedTime > secondsReport:
                    cancelMsg = "\nCancelling, please wait the current step to finish gracefully." if feedback.isCanceled() else ''
                    feedback.pushConsoleInfo("Elapsed " + str(round(totalTime)) + "s: " + waitMessage + cancelMsg)
                    elapsedTime = 0
                # if canCancelNow and feedback.isCanceled():
                #     feedback.pushConsoleInfo("Job starting to cancel.")
                #     job.cancel()
            feedback.pushConsoleInfo("Elapsed " + str(round(totalTime)) + "s on this step.")
            # UTILS.checkForCanceled(feedback)
            return job.result()

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

    @staticmethod
    def sendReport(dictParam):
        req = requests.get(url='http://csr.ufmg.br/imagery/save_reports.php?' + urlencode(dictParam))
        if req.status_code == HTTPStatus.OK:
            return req.text
        else:
            return ''

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

    # This function gets a system variable
    # it was necessary to use this instead of os.environ["PATH"] because QGIS overwrites the path variable
    # the win32 libraries appear not to be part of the standard python install, but they are included in the
    # python version that comes with QGIS
    @staticmethod
    def getenv_system(varname, default=''):
        try:
            import os
            import win32api
            import win32con
            v = default
            try:
                rkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE,
                                           'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment')
                try:
                    v = str(win32api.RegQueryValueEx(rkey, varname)[0])
                    v = win32api.ExpandEnvironmentStrings(v)
                except:
                    pass
            finally:
                win32api.RegCloseKey(rkey)
            return v
        except:
            return []

    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/12611523
    @staticmethod
    def which(program):
        fpath, fname = os.path.split(program)
        if fpath:
            if UTILS.is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if UTILS.is_exe(exe_file):
                    return exe_file
            for path in UTILS.getenv_system("PATH").split(os.pathsep):
                exe_file = os.path.join(path, program)
                if UTILS.is_exe(exe_file):
                    return exe_file

        return None

class UserInterrupted(Exception):
    pass

# class TimedMessageBox(QMessageBox):
#     def __init__(self, timeout, message, callback):
#         super(TimedMessageBox, self).__init__()
#         self.timeout = timeout
#         self.callback = callback
#
#     def intervalCallback(self):
#         self.callback()
#         QTimer().singleShot(self.timeout*1000, self.intervalCallback)
#
#     def showEvent(self, event):
#         QTimer().singleShot(self.timeout*1000, self.intervalCallback)
#         super(TimedMessageBox, self).showEvent(event)