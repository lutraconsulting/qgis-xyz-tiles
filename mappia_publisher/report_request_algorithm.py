from .OptionsCfg import OptionsCfg
from .UTILS import UTILS
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsLogger,
                       QgsProcessing,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsProcessingAlgorithm)


class ReportRequestAlgorithm(QgsProcessingAlgorithm):
    GITHUB_REPOSITORY = 'GITHUB_REPOSITORY'
    GITHUB_USER = 'GITHUB_USER'
    REPORT = 'REPORT'
    REASON = 'REASON'

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
                self.tr('Inform your github USERNAME (Please create a free account registering at https://github.com)'),
                optional=True,
                defaultValue=options['gh_user']
            )
        )


        self.addParameter(
            QgsProcessingParameterString(
                self.GITHUB_REPOSITORY,
                self.tr('The name of the "remote folder" (or repository in GIT).'),
                optional=True,
                defaultValue=options['gh_repository']
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.REPORT,
                self.tr('Please write report any issue or request a feature.'),
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.REASON,
                self.tr('Reason to like or dislike this plugin.\n\n(Your feedback is very important for us to improve our work)'),
                optional=True
            )
        )


    def checkParameterValues(self, parameters, context):

        repository = self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context)
        ghUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        report = self.parameterAsString(parameters, self.REPORT, context)
        reason = self.parameterAsString(parameters, self.REASON, context)

        if (not repository or not ghUser) and not report and not reason:
            return False, self.tr("Please fill the report first.")
        return super().checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        dictParam = {
            'repository': self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context),
            'ghUser': self.parameterAsString(parameters, self.GITHUB_USER, context),
            'report': self.parameterAsString(parameters, self.REPORT, context),
            'reason': self.parameterAsString(parameters, self.REASON, context)
        }
        return {"Response": UTILS.sendReport(dictParam)}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Report'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Feedback report')

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
        return ReportRequestAlgorithm()