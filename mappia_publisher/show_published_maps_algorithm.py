
from .OptionsCfg import OptionsCfg
from .GitHub import GitHub
from .WMSCapabilities import WMSCapabilities
from http import HTTPStatus
import webbrowser
import requests
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsLogger,
                       QgsProcessing,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsProcessingAlgorithm)


class ShowPublishedMapsAlgorithm(QgsProcessingAlgorithm):


    GITHUB_REPOSITORY = 'GITHUB_REPOSITORY'
    GITHUB_USER = 'GITHUB_USER'
    GITHUB_PASS = 'GITHUB_PASS'

    def initAlgorithm(self, config):

        #super(MappiaPublisherAlgorithm, self).initAlgorithm()
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        options = OptionsCfg.read()

        # We add the input vector features source. It can have any kind of
        # geometry.

        self.addParameter(
            QgsProcessingParameterString(
                self.GITHUB_USER,
                self.tr('Github USERNAME (Please create a free account registering at https://github.com)'),
                optional=False,
                defaultValue=options['gh_user']
            )
        )


        self.addParameter(
            QgsProcessingParameterString(
                self.GITHUB_REPOSITORY,
                self.tr('The name of the "remote folder" (or repository in GIT) where to identify the maps.'),
                optional=False,
                defaultValue=options['gh_repository']
            )
        )


    def checkParameterValues(self, parameters, context):
        curUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        if curUser and '@' in curUser:
            return False, self.tr("Please use your username instead of the email address.")
        return super().checkParameterValues(parameters, context)


    def processAlgorithm(self, parameters, context, feedback):
        ghUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        layerAttr = "1"
        ghRepository = self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context)
        storeUrl = GitHub.getGitUrl(ghUser, ghRepository)
        capabilitiesTxt = requests.get(url='https://raw.githubusercontent.com/'+ghUser+'/'+ghRepository+'/master/getCapabilities.xml')
        print(capabilitiesTxt.text)
        print("\n----------------------------------\n")
        foundMaps = []
        mapsUrl = "Sorry, no maps were found."
        if not GitHub.existsRepository(ghUser, ghRepository):
            feedback.pushConsoleInfo("Sorry, the selected repository was not found. (" + storeUrl + ")")
        elif capabilitiesTxt.status_code == HTTPStatus.OK:
            foundMaps = WMSCapabilities.getAllLayers(capabilitiesTxt.text)
            if len(foundMaps) <= 0:
                feedback.pushConsoleInfo("Sorry, there are no maps in this repository.")
                return
            feedback.pushConsoleInfo("Found the following maps: " + '\n'.join(foundMaps))
            options = OptionsCfg.read()
            if not options[OptionsCfg.ZOOM_MAX]:
                options[OptionsCfg.ZOOM_MAX] = 7
            mapsUrl = "https://maps.csr.ufmg.br/calculator/?queryid=152&storeurl=" + storeUrl + "/&zoomlevels=" + str(options[OptionsCfg.ZOOM_MAX]) + "&remotemap=" + ",".join([layer + ";" + layerAttr for layer in foundMaps])
            feedback.pushConsoleInfo("The following maps were found into the repository \"" + storeUrl + "\":" + '\n'.join(foundMaps) + "\n---------")
            feedback.pushConsoleInfo(mapsUrl)
            webbrowser.open_new(mapsUrl)
        elif capabilitiesTxt.status_code == HTTPStatus.NOT_FOUND:
            feedback.pushConsoleInfo("Sorry, no map is shared from this repository.")
        else:
            feedback.pushConsoleInfo("Error: Please confirm the user or repository. ERROR response_code: " + str(capabilitiesTxt.status_code) + " response: " + str(capabilitiesTxt.text))
        return {"MAPS": foundMaps, "SHAREABLE_URL": mapsUrl}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'View'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Online mapping'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ShowPublishedMapsAlgorithm()