import os
import json
from datetime import date

class OptionsCfg:
    UPDATE_CHECK = 'update_check'
    ZOOM_MAX = 'zoom_max'
    GIT_EXE = "git_exe"
    ATTR_NAME = "attrName"
    GH_USER = "gh_user"
    GH_REPOSITORY = "gh_repository"
    FOLDER = "folder"
    # GH_PASS = "gh_pass"
    INCLUDE_DL = 'include_dl'
    ASK_USER = 'ask_user'

    # https://gis.stackexchange.com/questions/130027/getting-a-plugin-path-using-python-in-qgis
    @staticmethod
    def resolve(name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

    @staticmethod
    def createCfg(zoom_max=None, gitExe=None, attrName=None, ghUser=None, ghRepository=None, folder=None, includeDl=None, askUser=None, update_check=None):
        defaults = dict()
        defaults[OptionsCfg.UPDATE_CHECK] = update_check if update_check is not None else None
        defaults[OptionsCfg.ZOOM_MAX] = zoom_max if zoom_max is not None else 9
        defaults[OptionsCfg.GIT_EXE] = gitExe if gitExe is not None else ''
        defaults[OptionsCfg.ATTR_NAME] = attrName if attrName is not None else '1'
        defaults[OptionsCfg.GH_USER] = ghUser if ghUser is not None else ''
        defaults[OptionsCfg.GH_REPOSITORY] = ghRepository if ghRepository is not None else ''
        defaults[OptionsCfg.FOLDER] = folder if folder is not None else ''
        defaults[OptionsCfg.INCLUDE_DL] = (includeDl in ['True', '1', True, 'true']) if includeDl is not None else ''
        defaults[OptionsCfg.ASK_USER] = askUser if askUser is not None else False
        return defaults


    @staticmethod
    def write(zoom_max, gitExe, attrName, ghUser, ghRepository, folder, includeDl, askUser, update_check):
        with open(OptionsCfg.resolve("options.json"), 'w', encoding="utf-8") as f:
            json.dump(OptionsCfg.createCfg(zoom_max, gitExe, attrName, ghUser, ghRepository, folder, includeDl, askUser, update_check), f)

    @staticmethod
    def get(propertyName):
        return OptionsCfg.read()[propertyName]

    @staticmethod
    def read():
        with open(OptionsCfg.resolve("options.json"), 'r', encoding="utf-8") as f:
            cfg = json.load(f)
            defaults = OptionsCfg.createCfg()
            for key in cfg.keys():
                defaults[key] = cfg[key]
        return defaults

