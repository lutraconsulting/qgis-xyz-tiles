# from mappia_publisher.mappia_publisher.test.utilities import get_qgis_app
#
# (QGIS_APP, CANVAS, IFACE, PARENT) = get_qgis_app()
import xmltodict
content = ""
with open('F:/Danilo/Programacao/python/mappia_publisher/mappia_publisher/mappia_publisher/test/data/xmlWithoutZoomMax.xml') as fd:
    content = xmltodict.parse(fd.read())

