
from . import xmltodict
from .UTILS import UTILS
from collections import OrderedDict
from qgis.PyQt.QtWidgets import QMessageBox
import collections
from pathlib import Path
import json
import os
import re

from qgis.core import (QgsCoordinateReferenceSystem, QgsProject, QgsPointXY, QgsCoordinateTransform)

class WMSCapabilities:

    @staticmethod
    def getDefaultCapabilities():
        return '''<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE WMT_MS_Capabilities SYSTEM "http://maps.csr.ufmg.br:80/geoserver/schemas/wms/1.1.1/WMS_MS_Capabilities.dtd"[
    <!ELEMENT VendorSpecificCapabilities (TileSet*) >
    <!ELEMENT TileSet (SRS, BoundingBox?, Resolutions, Width, Height, Format, Layers*, Styles*) >
    <!ELEMENT Resolutions (#PCDATA) >
    <!ELEMENT Width (#PCDATA) >
    <!ELEMENT Height (#PCDATA) >
    <!ELEMENT Layers (#PCDATA) >
    <!ELEMENT Styles (#PCDATA) >
    ]>
    <WMT_MS_Capabilities version="1.1.1" updateSequence="63258">
      <Service>
        <Name>OGC:WMS</Name>
        <Title>CSR Web Map Service</Title>
        <Abstract>Compliant WMS Response</Abstract>
        <KeywordList>
          <Keyword>WFS</Keyword>
          <Keyword>WMS</Keyword>
          <Keyword>GEOSERVER</Keyword>
        </KeywordList>
        <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://geoserver.sourceforge.net/html/index.php"/>
        <ContactInformation>
          <ContactPersonPrimary>
            <ContactPerson>GITHUB owner</ContactPerson>
            <ContactOrganization>GITHUB owner</ContactOrganization>
          </ContactPersonPrimary>
          <ContactPosition>Chief geographer</ContactPosition>
          <ContactAddress>
            <AddressType>Work</AddressType>
            <Address/>
            <City>Alexandria</City>
            <StateOrProvince/>
            <PostCode/>
            <Country>Egypt</Country>
          </ContactAddress>
          <ContactVoiceTelephone/>
          <ContactFacsimileTelephone/>
          <ContactElectronicMailAddress>claudius.ptolomaeus@gmail.com</ContactElectronicMailAddress>
        </ContactInformation>
        <Fees>NONE</Fees>
        <AccessConstraints>NONE</AccessConstraints>
      </Service>
      <Capability>
        <Request>
          <GetCapabilities>
            <Format>application/vnd.ogc.wms_xml</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
                <Post>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Post>
              </HTTP>
            </DCPType>
          </GetCapabilities>
          <GetMap>
            <Format>image/png</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
              </HTTP>
            </DCPType>
          </GetMap>
          <GetFeatureInfo>
            <Format>text/plain</Format>
            <Format>application/vnd.ogc.gml</Format>
            <Format>application/vnd.ogc.gml/3.1.1</Format>
            <Format>text/html</Format>
            <Format>application/json</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
                <Post>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Post>
              </HTTP>
            </DCPType>
          </GetFeatureInfo>
          <DescribeLayer>
            <Format>application/vnd.ogc.wms_xml</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
              </HTTP>
            </DCPType>
          </DescribeLayer>
          <GetLegendGraphic>
            <Format>image/png</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
              </HTTP>
            </DCPType>
          </GetLegendGraphic>
          <GetStyles>
            <Format>application/vnd.ogc.sld+xml</Format>
            <DCPType>
              <HTTP>
                <Get>
                  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="http://maps.csr.ufmg.br:80/geoserver/wms?SERVICE=WMS&amp;"/>
                </Get>
              </HTTP>
            </DCPType>
          </GetStyles>
        </Request>
        <Exception>
          <Format>application/vnd.ogc.se_xml</Format>
          <Format>application/vnd.ogc.se_inimage</Format>
        </Exception>
        <VendorSpecificCapabilities>
        </VendorSpecificCapabilities>
        <UserDefinedSymbolization SupportSLD="1" UserLayer="1" UserStyle="1" RemoteWFS="1"/>
        <Layer queryable="0" opaque="0" noSubsets="0">
          <Title>MapServer via GItHub</Title>
          <Abstract>GitHub WMS</Abstract>
          <!--All supported EPSG projections:-->
          <SRS>EPSG:3857</SRS>
          <SRS>EPSG:4326</SRS>
          <SRS>EPSG:900913</SRS>
          <SRS>EPSG:42303</SRS>
          <LatLonBoundingBox minx="-180.00004074199998" miny="-90.0" maxx="180.0000000000001" maxy="90.0"/>
        </Layer>
      </Capability>
    </WMT_MS_Capabilities>'''

    @staticmethod
    def convertCoordinateProj(crsProj, fromX, fromY, outputProjected):

        regex = r"^[ ]*PROJCS"
        isProjected = re.match(regex, crsProj)

        if (isProjected and outputProjected) or ( not isProjected and  not outputProjected):
            return (fromX, fromY)
        else:
            fProj = QgsCoordinateReferenceSystem()
            fProj.createFromWkt(crsProj)
            tProj = QgsCoordinateReferenceSystem()
            tProj.createFromProj4("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs" if outputProjected else "+proj=longlat +datum=WGS84 +no_defs ")
            newCoord = QgsCoordinateTransform(fProj, tProj, QgsProject.instance()).transform(QgsPointXY(fromX, fromY), True)
        return (newCoord.x, newCoord.y)

    @staticmethod
    def getMapDescription(layerNameID, layerAttr, latMinX, latMinY, latMaxX, latMaxY, projMinX, projMinY, projMaxX, projMaxY):
        layerAttr = UTILS.normalizeName(layerAttr)
        layerNameID = UTILS.normalizeName(layerNameID)
        # Inverti o minx/miny e maxX/maxY do epsg 4326 pq estava trocando no geoserver, mas n sei pq isso acontece.
        return """<CONTENT>
          <Layer queryable="1" opaque="0">
          <Name>GH:""" + layerNameID + """</Name>
          <Title>""" + layerNameID + """</Title>
          <Abstract>GH:""" + layerNameID + """ ABSTRACT</Abstract>
          <KeywordList>
            <Keyword>GITHUB</Keyword>
          </KeywordList>
          <SRS>EPSG:4326</SRS>
          <LatLonBoundingBox minx=\"""" + str(latMinX) + """\" miny=\"""" + str(latMinY) + """\" maxx=\"""" + str(
            latMaxX) + """\" maxy=\"""" + str(latMaxY) + """\"/>
          <BoundingBox SRS="EPSG:4326" minx=\"""" + str(projMinX) + """\" miny=\"""" + str(
            projMinY) + """\" maxx=\"""" + str(projMaxX) + """\" maxy=\"""" + str(projMaxY) + """\"/>
          <Style>
           <Name>""" + layerAttr + """</Name>
           <Title>""" + layerAttr + """</Title>
           <Abstract/>
           <LegendURL width="20" height="20">
           <Format>image/png</Format>
           <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:type="simple" xlink:href="https://maps.csr.ufmg.br:443/geoserver/wms?request=GetLegendGraphic&amp;format=image%2Fpng&amp;width=20&amp;height=20&amp;layer=""" + layerNameID + """\"/>
           </LegendURL>
          </Style>
        </Layer>
        </CONTENT>
        """

    @staticmethod
    def getTileSetDescription(fileNameId, latMinX, latMinY, latMaxX, latMaxY, projMinX, projMinY, projMaxX, projMaxY):
        # <BoundingBox SRS="EPSG:4326" minx=\"""" + str(latMinX) + """\" miny=\"""" + str(latMinY) + """\" maxx=\"""" + str(latMaxX) + """\" maxy=\"""" + str(latMaxY) + """\"/>
        return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
        <CONTENT>
          <TileSet>
            <SRS>EPSG:4326</SRS>
            <BoundingBox SRS="EPSG:4326" minx="-180.0" miny="-90.0" maxx="0.0" maxy="90.0"/>
        <Resolutions>0.703125 0.3515625 0.17578125 0.087890625 0.0439453125 0.02197265625 0.010986328125 0.0054931640625 0.00274658203125 0.001373291015625 6.866455078125E-4 3.4332275390625E-4 1.71661376953125E-4 8.58306884765625E-5 4.291534423828125E-5 2.1457672119140625E-5 1.0728836059570312E-5 5.364418029785156E-6 2.682209014892578E-6 1.341104507446289E-6 6.705522537231445E-7 3.3527612686157227E-7 </Resolutions>
            <Width>256</Width>
            <Height>256</Height>
            <Format>image/png</Format>
            <Layers>GH:""" + fileNameId + """</Layers>
            <Styles/>
          </TileSet>
          <TileSet>
            <SRS>EPSG:900913</SRS>
            <BoundingBox SRS="EPSG:900913" minx="-2.003750834E7" miny="-2.003750834E7" maxx="2.003750834E7" maxy="2.003750834E7"/>
        <Resolutions>156543.03390625 78271.516953125 39135.7584765625 19567.87923828125 9783.939619140625 4891.9698095703125 2445.9849047851562 1222.9924523925781 611.4962261962891 305.74811309814453 152.87405654907226 76.43702827453613 38.218514137268066 19.109257068634033 9.554628534317017 4.777314267158508 2.388657133579254 1.194328566789627 0.5971642833948135 0.29858214169740677 0.14929107084870338 0.07464553542435169 0.037322767712175846 0.018661383856087923 0.009330691928043961 0.004665345964021981 0.0023326729820109904 0.0011663364910054952 5.831682455027476E-4 2.915841227513738E-4 1.457920613756869E-4 </Resolutions>
            <Width>256</Width>
            <Height>256</Height>
            <Format>image/png</Format>
            <Layers>GH:""" + fileNameId + """</Layers>
            <Styles/>
          </TileSet>
          </CONTENT>
        """
        # <BoundingBox SRS="EPSG:900913" minx=\"""" + str(projMinX) + """\" miny=\"""" + str(projMinY) + """\" maxx=\"""" + str(projMaxX) + """\" maxy=\"""" + str(projMaxY) + """\"/>

    @staticmethod
    def getAllLayers(content, layerAttr='1'):
        #FIXME should use the style name to identify the layer attributes
        doc = xmltodict.parse(content)
        layerDefinitions = doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer']
        if layerDefinitions is not None and isinstance(layerDefinitions, list) and len(layerDefinitions):
            allLayers = [curLayer["Name"] for curLayer in layerDefinitions]
        elif layerDefinitions is not None and isinstance(doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer'], collections.OrderedDict) and len(layerDefinitions):
            allLayers = [layerDefinitions["Name"]]
        else:
            allLayers = []
        return allLayers

    @staticmethod
    def getOperationsListForCustomLayer(docLayer):
        #FIXME Não deveria modificar o input numa funcao de get
        #FIXME codigo duplicado
        if not "Operation" in docLayer:
            docLayer["Operation"] = []
        elif isinstance(docLayer["Operation"], collections.OrderedDict):
            docLayer["Operation"] = [docLayer["Operation"]]

        if len(docLayer["Operation"]) == 0:
            return []
        elif isinstance(docLayer["Operation"], str):
            raise Exception(json.dumps(docLayer))
        else:
            return [{'type': operation["@type"], 'attribute': operation["#text"]} for operation in docLayer['Operation']]


    @staticmethod
    def getAllCustomLayers(content, layerAttr='1'):
        doc = xmltodict.parse(content)
        allCustomLayers = []
        if 'CustomLayer'  in doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']:
            layerDefinitions = doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['CustomLayer']

            if layerDefinitions is not None and isinstance(layerDefinitions, collections.OrderedDict):
                layerDefinitions = [layerDefinitions]
            if layerDefinitions is not None and isinstance(layerDefinitions, list) and len(layerDefinitions) > 0:
                for curLayer in layerDefinitions:
                    for operation in WMSCapabilities.getOperationsListForCustomLayer(curLayer):
                        allCustomLayers.append(curLayer["Name"] + ";" + operation['attribute'])
                        #allCustomLayers.append(curLayer["Name"] + ":" + operation['attribute'] + ":" + operation['type'])
        return allCustomLayers

    @staticmethod
    def getCurrentCapabilitiesDoc(directory):
        capabilitiesPath = os.path.join(directory, "getCapabilities.xml")
        if os.path.isfile(capabilitiesPath):
            capabilitiesContent = Path(capabilitiesPath).read_text()
        else:
            capabilitiesContent = WMSCapabilities.getDefaultCapabilities()
        doc = xmltodict.parse(capabilitiesContent)
        return doc

    @staticmethod
    def saveCurrentCapabilities(directory, doc):
        capabilitiesPath = os.path.join(directory, "getCapabilities.xml")
        Path(capabilitiesPath).write_text(xmltodict.unparse(doc, pretty=True))

    @staticmethod
    def getCustomLayerDefaultDefinition(layerName):
        layerName = UTILS.normalizeName(layerName)
        return xmltodict.parse("""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
            <CONTENT>
                <Name>GH:""" + layerName + """</Name>
                <Title>"""+layerName +"""</Title>
            </CONTENT>""")["CONTENT"]

    #customDoc é um Dict vindo do xmltodict. layerAttr e operation são strings
    @staticmethod
    def addOperation(customDoc, layerAttr, operation):
        layerAttr = UTILS.normalizeName(layerAttr)
        if not "Operation" in customDoc:
            customDoc["Operation"] = list()
        if isinstance(customDoc["Operation"], collections.OrderedDict):
            customDoc["Operation"] = [customDoc["Operation"]]

        found = False
        for curOperationDict in customDoc["Operation"]:
            if not found and '@type' in curOperationDict and curOperationDict['@type'] == operation and curOperationDict['#text'] == layerAttr:
                found = True
        if not found:
            customDoc['Operation'].append(xmltodict.parse("""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
                            <CONTENT>
                            <Operation type=\"""" + operation + """\">""" + layerAttr + """</Operation>
                            </CONTENT>""")["CONTENT"]["Operation"])
        return customDoc


    @staticmethod
    def updateCustomXML(directory, layerTitle, layerAttr, operation):
        doc = WMSCapabilities.getCurrentCapabilitiesDoc(directory)
        filename = UTILS.normalizeName(layerTitle)  # layer Name no qgis

        if 'CustomLayer' in doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']:
            if type(doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"]) is collections.OrderedDict:
                curLayer = doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"]
                doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"] = [curLayer]
        else:
            doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['CustomLayer'] = []

        curLayerDefinition = None
        if 'CustomLayer' in doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']:
            for iLayer in range(len(doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"]) - 1, -1, -1):
                curLayer = doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"][iLayer]
                if "Name" in curLayer and filename in curLayer["Name"]:
                    doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"].pop(iLayer)
                    curLayerDefinition = curLayer
                    #TODO verificar se não restaram outros com mesmo nome.
        if curLayerDefinition is None:
            curLayerDefinition = WMSCapabilities.getCustomLayerDefaultDefinition(filename)
        WMSCapabilities.addOperation(curLayerDefinition, layerAttr, operation)
        doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']["CustomLayer"].append(curLayerDefinition)
        WMSCapabilities.saveCurrentCapabilities(directory, doc)


    @staticmethod
    def updateXML(directory, layer, layerTitle, layerAttr):
        doc = WMSCapabilities.getCurrentCapabilitiesDoc(directory)

        filename = UTILS.normalizeName(layerTitle) #layer Name no qgis

        #extents, projection
        projMaxX = layer.extent().xMaximum()
        projMinX = layer.extent().xMinimum()
        projMaxY = layer.extent().yMaximum()
        projMinY = layer.extent().yMinimum()
        llExtent = UTILS.getMapExtent(layer, QgsCoordinateReferenceSystem('EPSG:4326'))
        latMaxX = llExtent.xMaximum()
        latMinX = llExtent.xMinimum()
        latMaxY = llExtent.yMaximum()
        latMinY = llExtent.yMinimum()


        if 'Layer' in doc['WMT_MS_Capabilities']['Capability']['Layer']:
            if type(doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer']) is collections.OrderedDict:
                curLayer = doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer']
                doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer'] = [curLayer]

        if 'Layer' in doc['WMT_MS_Capabilities']['Capability']['Layer']:
            for iLayer in range(len(doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer']) - 1, -1, -1):
                curLayer = doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer'][iLayer]
                if "Name" in curLayer and curLayer["Name"] == "GH:" + filename:
                    doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer'].pop(iLayer)

        #FIXME One attribute only. (Is always overwriting)
        newLayerDescription = xmltodict.parse(
            WMSCapabilities.getMapDescription(filename, layerAttr, latMinX, latMinY, latMaxX, latMaxY,
                                              projMinX, projMinY, projMaxX, projMaxY))['CONTENT']
        if 'Layer' in doc['WMT_MS_Capabilities']['Capability']['Layer']:
            doc['WMT_MS_Capabilities']['Capability']['Layer']['Layer'].append(newLayerDescription['Layer'])
        else:
            doc['WMT_MS_Capabilities']['Capability']['Layer'] = newLayerDescription

        newTileSetDescription = xmltodict.parse(
            WMSCapabilities.getTileSetDescription(filename, latMinX, latMinY, latMaxX, latMaxY, projMinX, projMinY,
                                                  projMaxX, projMaxY))['CONTENT']

        if doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities'] is not None and 'TileSet' in \
                doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']:
            if type(doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities'][
                        'TileSet']) is collections.OrderedDict:
                curTileSet = doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet']
                doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet'] = [
                    curTileSet]  # Transforms into a list

        if doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities'] is not None and 'TileSet' in \
                doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']:
            for iTileSet in range(
                    len(doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet']) - 1,
                    -1, -1):
                curTileSet = doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet'][iTileSet]
                if "Layers" in curTileSet and curTileSet["Layers"] == "GH:" + filename:
                    doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet'].pop(iTileSet)
            doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities']['TileSet'] += newTileSetDescription[
                'TileSet']  # Dois elementos c mesma chave representa com lista
        else:
            doc['WMT_MS_Capabilities']['Capability']['VendorSpecificCapabilities'] = newTileSetDescription
        WMSCapabilities.saveCurrentCapabilities(directory, doc)
