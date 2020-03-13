import json

folder = "C:\\Danilo\\Temp\\mappia_usage_example\\"
allObjs = []
for file in [folder + file for file in ["netimoveis.json", "vivareal.json", "zapimoveis.json"]]:
    with open(file, 'r') as jsonFile:
        allObjs = allObjs + json.load(jsonFile)

with open(folder + "all.json", 'w') as jsonResult:
    json.dump(allObjs, jsonResult)