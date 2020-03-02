import requests
import json
import webbrowser


def createNewToken():
    keyName = "Mappia Access"
    payload = {
        "scopes": [
            "repo",
            "write:org"
        ],
        "note": keyName
    }

    result = requests.post(url="https://api.github.com/authorizations", data=json.dumps(payload),
                           headers={"Accept": "application/json"}, auth=('asfixia', 'Dan33122191'))
    print(result.content)

    resultDict = json.loads(result.text)
    if "token" in resultDict:
        return resultDict["token"]
    elif "errors" in resultDict and len(resultDict["errors"]) > 0 and "code" in resultDict["errors"][0] and "exists" in resultDict["errors"][0]["code"]:
        raise Exception("Error: The key was already generated, please enter your key or delete the older if you lost the older key. Visit the site : https://github.com/settings/tokens and delete the key named '" + keyName + "' on the given site and try again.")
    else:
        return Exception("Unkown error, given response is: " + result.text)
    token = '4fc245f946793a1fed4af2a1ea09bd2a191cfcd8'
    return token

#requests.get(url='https://github.com/login/oauth/authorize?client_id=asfixia&scopes=repo%20write:org&state=something-random')