# import collections
import time;

layer = iface.mapCanvas().layers()[0]

clonedLayer = layer.clone()
layerRenderer = clonedLayer.renderer()
renderContext = QgsRenderContext()
renderContext.setUseAdvancedEffects(True)
renderContext.setFlags(QgsRenderContext.Flag.Antialiasing)
imageList = list()
iconField = QgsField('icon_url', QVariant.String, 'text')
clonedLayer.startEditing()
res = clonedLayer.addAttribute(iconField)
clonedLayer.commitChanges()
clonedLayer.startEditing()
for feature in clonedLayer.getFeatures():
    layerRenderer.startRender(renderContext, clonedLayer.fields())
    symbol = layerRenderer.originalSymbolsForFeature(feature, renderContext)
    if len(symbol) <= 0:
        continue
    else:
        symbol = symbol[0]
    layerRenderer.stopRender(renderContext)
    curImage = symbol.asImage(QSize(32, 32))
    try:
        imgIndex = imageList.index(curImage)
    except Exception as e:
        imageList.append(curImage)
        imgIndex = len(imageList) - 1
    feature.setAttribute("icon_url", './' + str(imgIndex) + ".png")
    clonedLayer.updateFeature(feature)

clonedLayer.commitChanges()
wgs_crs = QgsCoordinateReferenceSystem('EPSG:4326')
QgsVectorFileWriter.writeAsVectorFormat(clonedLayer, 'C:/Users/danilo/Downloads/symbol/myjson_danilo_.json',
                                        'utf-8', wgs_crs, 'CSV', layerOptions=['GEOMETRY=AS_XY'])
for index in range(len(imageList)):
    imageList[index].save('C:/Users/danilo/Downloads/symbol/' + str(index) + '.png')

