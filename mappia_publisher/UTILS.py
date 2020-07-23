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
    def getQGISversion():
        try:
            from qgis.core import Qgis
            return Qgis.QGIS_VERSION
        except:
            return None

    @staticmethod
    def isQgisSupported():
        try:
            return int(UTILS.getQGISversion()[0]) >= 3
        except:
            return True

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
            return ''

    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    @staticmethod
    def getGitDefault(gitExe):
        if gitExe and len(gitExe) > 0 and UTILS.is_exe(gitExe):
            return gitExe
        elif UTILS.which("git") is not None:
            return UTILS.which("git")
        elif UTILS.which("git.exe") is not None:
            return UTILS.which("git.exe")
        elif UTILS.which("bin\\git.exe") is not None:
            return UTILS.which("bin\\git.exe")
        for curPath in ['C:\\Program Files\\Git\\bin\\git.exe', '/usr/bin/git', 'C:\\Program Files (x86)\\SmartGit\\git\\bin\\git.exe', os.environ['USERPROFILE'] if 'USERPROFILE' in os.environ else '' + '\\AppData\\Local\\Programs\\Git\\git.exe', (os.environ['USERPROFILE'] if 'USERPROFILE' in os.environ else '') + '\\AppData\\Local\\Programs\\Git\\bin\\git.exe']:
            if UTILS.is_exe(curPath):
                return curPath
        else:
            return ''

    # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/12611523
    @staticmethod
    def which(program):
        if program and UTILS.is_exe(program):
            return program
        elif not which(program) is None:
            return which(program)
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if UTILS.is_exe(exe_file):
                    return exe_file
            for path in UTILS.getenv_system("PATH").split(os.pathsep): #windows
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

# -*- coding: utf-8 -*-

__author__ = "Daniel Roy Greenfeld"
__email__ = "pydanny@gmail.com"
__version__ = "0.6.1"

import os
import sys

try:  # Forced testing
    from shutil import which
except ImportError:  # Forced testing
    # Versions prior to Python 3.3 don't have shutil.which

    def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        """Given a command, mode, and a PATH string, return the path which
        conforms to the given mode on the PATH, or None if there is no such
        file.
        `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
        of os.environ.get("PATH"), or can be overridden with a custom search
        path.
        Note: This function was backported from the Python 3 source code.
        """
        # Check that a given file can be accessed with the correct mode.
        # Additionally check that `file` is not a directory, as on Windows
        # directories pass the os.access check.

        def _access_check(fn, mode):
            return os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn)

        # If we're given a path with a directory part, look it up directly
        # rather than referring to PATH directories. This includes checking
        # relative to the current directory, e.g. ./script
        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd

            return None

        if path is None:
            path = os.environ.get("PATH", os.defpath)
        if not path:
            return None

        path = path.split(os.pathsep)

        if sys.platform == "win32":
            # The current directory takes precedence on Windows.
            if os.curdir not in path:
                path.insert(0, os.curdir)

            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path
            # extensions. This will allow us to short circuit when given
            # "python.exe". If it does match, only test that one, otherwise we
            # have to try others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext.lower() for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]

        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if normdir not in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(dir, thefile)
                    if _access_check(name, mode):
                        return name

        return None