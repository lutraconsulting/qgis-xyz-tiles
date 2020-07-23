import re
import os
import random
import tempfile
import webbrowser
import subprocess
import requests
import time
import json
import glob
import platform
from http import HTTPStatus
from requests import request
from datetime import datetime
from time import sleep
from .UTILS import UTILS
from qgis.PyQt.QtWidgets import QMessageBox

class GitHub:

    originName = "mappia"
    releaseName = "Map_Download"
    githubApi = 'https://api.github.com/'

    personal_token = ''

    @staticmethod
    def testLogin(user, token):
        return requests.get(url=GitHub.githubApi + 'user', auth=(user, token)).status_code == 200

    @staticmethod
    def prepareEnvironment(gitExecutable):
        if not gitExecutable:
            return
        gitProgramFolder = os.path.dirname(gitExecutable)
        #feedback.pushConsoleInfo(gitProgramFolder) #cinza escondido
        #feedback.setProgressText(gitExecutable) #preto
        os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = gitExecutable
        #initialPath = os.environ['PATH']
        os.environ['GIT_PYTHON_REFRESH'] = 'quiet'
        import git
        git.refresh(gitExecutable)
        try:
            os.environ['PATH'].split(os.pathsep).index(gitProgramFolder)
        except:
            os.environ["PATH"] = gitProgramFolder + os.pathsep + os.environ["PATH"]

    @staticmethod
    def install_git(mustAskUser):
        def userConfirmed():
            return QMessageBox.Yes == QMessageBox.question(None, "Required GIT executable was not found",
                                                           "Click 'YES' to start download and continue, otherwise please select the executable manually.",
                                                           defaultButton=QMessageBox.Yes,
                                                           buttons=(
                                                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))

        return 'AAAAAAAA CARAI'
        if not ("Windows" in platform.system() or "CYGWIN_NT" in platform.system()):
            QMessageBox.question(None, "Error: Required GIT executable was not found", "Please install git in your system and fill the parameter GIT executable path.")
            return 'UAAAAAAAAAAA'
        elif mustAskUser and not userConfirmed():
            return 'UEEEEEEEEEEEEEE'

        def download_file(url, toDir):
            local_filename = os.path.join(toDir, url.split('/')[-1])
            # NOTE the stream=True parameter below
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
            return local_filename

        tmpDir = tempfile.mkdtemp()
        gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.25.1.windows.1/PortableGit-2.25.1-64-bit.7z.exe"
        # QMessageBox.information(None, "Starting GIT download", "This step will take some time, it depends on your internet speed.\nClick 'OK' to continue.", defaultButton=QMessageBox.Ok, buttons=QMessageBox.Ok)
        selfExtractor = download_file(gitUrl, tmpDir)
        portableGit = os.path.join(tmpDir, "portablegit")
        if (not os.path.isfile(selfExtractor)):
            return 'UUCCCCCCCCCC'
        subprocess.check_output([selfExtractor, '-o', portableGit, "-y"])
        return os.path.join(portableGit, 'mingw64', 'bin', 'git.exe')

    @staticmethod
    def getGitExe():
        gitExe = ''
        try:
            gitExe = os.environ['GIT_PYTHON_GIT_EXECUTABLE']
        except:
            pass
        return gitExe

    @staticmethod
    def getRepositorySize(user, repository, password):
        response = GitHub._request('GET', 'https://api.github.com/repos/' + user + "/" + repository, token=password,
                                   headers={'Content-Type': 'application/json'})
        try:
            if response.status_code == 200:
                return json.loads(response.content)['size']
        except:
            print("Failed to get the repository size, ignoring it.")
            return None
        return None

    @staticmethod
    def getGitUrl(githubUser, githubRepository):
        return "https://github.com/" + githubUser + "/" + githubRepository + "/"

    #No password to allow using configured SSHKey.
    @staticmethod
    def getGitPassUrl(user, repository, password):
        if password is None or not password:
            return GitHub.getGitUrl(user, repository)
        return "https://" + user + ":" + password + "@github.com/" + user + "/" + repository + "/"

    @staticmethod
    def lsremote(url):
        import git
        remote_refs = {}
        g = git.cmd.Git()
        for ref in g.ls_remote(url).split('\n'):
            hash_ref_list = ref.split('\t')
            remote_refs[hash_ref_list[1]] = hash_ref_list[0]
        return remote_refs

    @staticmethod
    def existsRepository(user, repository):
        try:
            #feedback.pushConsoleInfo("URL: " + GitHub.getGitUrl(user, repository))
            resp = requests.get(GitHub.getGitUrl(user, repository))
            if resp.status_code == 200:
                return True
            else:
                return False
            #result = GitHub.lsremote(GitHub.getGitUrl(user, repository))
        except:
            return False

    @staticmethod
    def configUser(repo, user):
        repo.git.config("user.email", user)
        repo.git.config("user.name", user)

    @staticmethod
    def getRepository(folder, user, repository, password, feedback):
        from git import Repo
        from git import InvalidGitRepositoryError

        # #Não está funcionando a validação #FIXME Repository creation verification is not working (Modify the create Repo function to verify the creation)
        # #feedback.pushConsoleInfo(user + ' at ' + repository)
        # if not GitHub.existsRepository(user, repository):
        #     feedback.pushConsoleInfo("The repository " + repository + " doesn't exists.\nPlease create a new one at https://github.com/new .")
        #     return None

        #Cria ou pega o repositório atual.
        repo = None
        if not os.path.exists(folder) or (os.path.exists(folder) and not os.listdir(folder)):
            repoSize = GitHub.getRepositorySize(user, repository, password)
            if repoSize is not None:
                repoSize = str(repoSize) + "(kb)"
            else:
                repoSize = ''
            feedback.pushConsoleInfo("Cloning git repository: " + GitHub.getGitUrl(user, repository) + "\nPlease wait, it will download all maps in your repository. " + repoSize)
            repo = GitInteractive.cloneRepo(user, repository, folder, feedback)#Repo.clone_from(GitHub.getGitUrl(user, repository), folder, recursive=True, progress=GitHub.getGitProgressReport(feedback))
            assert (os.path.exists(folder))
            assert(repo)
        else:
            try:
                repo = Repo(folder)
                repoUrl = repo.git.remote("-v")
                expectedUrl = GitHub.getGitUrl(user, repository)
                if repoUrl and not (expectedUrl in re.compile("[\\n\\t ]").split(repoUrl)):
                    feedback.pushConsoleInfo("Your remote URL " + repoUrl + " does not match the expected url " + expectedUrl)
                    return False
            except InvalidGitRepositoryError as e:
                feedback.pushConsoleInfo("The destination folder must be a repository or an empty folder. Reason: " + str(e))
                #repo = Repo.init(folder, bare=False)
        return repo

    @staticmethod
    def isOptionsOk(folder, user, repository, feedback, ghPassword=None, mustAskUser=False):
        try:
            #Cria ou pega o repositório atual.
            repo = GitHub.getRepository(folder, user, repository, ghPassword, feedback)
            if not repo:
                return False
            GitHub.configUser(repo, user)
            if repo.git.status("--porcelain"):
                response = not mustAskUser or QMessageBox.question(None, "Local repository is not clean.",
                                     "The folder have local changes, we need to fix to continue.\nClick 'DISCARD' to discard changes, 'YES' to commit changes, otherwise click 'CANCEL' to cancel and resolve manually.",
                                     buttons=(QMessageBox.Discard | QMessageBox.Yes | QMessageBox.Cancel),
                                     defaultButton=QMessageBox.Discard)
                if not mustAskUser or response == QMessageBox.Yes:
                    feedback.pushConsoleInfo("Pulling remote repository changes to your directory.")
                    GitHub.tryPullRepository(repo, user, repository, feedback)  # Danilo
                    feedback.pushConsoleInfo("Adding all files in folder")
                    GitHub.addFiles(repo, user, repository, feedback)
                    feedback.pushConsoleInfo("Adding all files in folder")
                    GitHub.gitCommit(repo, msg="QGIS - Adding all files in folder " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"), feedback=feedback)
                    feedback.pushConsoleInfo("QGIS - Sending changes to Github")
                    # try:
                    #     UTILS.runLongTask(repo.git.pull, feedback, 'Pease wait, pulling changes.', 30)
                    # except:
                    #     pass
                    GitHub.pushChanges(repo, user, repository, ghPassword, feedback)
                elif response == QMessageBox.Discard:
                    repo.git.clean("-df")
                    repo.git.checkout('--', '.')
                else:
                    feedback.pushConsoleInfo("Error: Local repository is not clean.\nPlease commit the changes made to local repository before run.\nUse: git add * and git commit -m \"MSG\"")
                    return False
            else:
                try:
                    GitHub.tryPullRepository(repo, user, repository, feedback)
                    feedback.pushConsoleInfo("Git: Checking out changes.")
                    repo.git.checkout('--', '.')
                except:
                    pass
            return True
        except Exception as ex:
            feedback.pushConsoleInfo("Canceled due to: {0}".format(ex))
            return False

    @staticmethod
    def findGitExe(gitExe, found_git, mustAskUser):
        if gitExe and UTILS.is_exe(gitExe):
            return gitExe
        elif ('GIT_PYTHON_GIT_EXECUTABLE' in os.environ) and UTILS.is_exe(os.environ['GIT_PYTHON_GIT_EXECUTABLE']):
            return os.environ['GIT_PYTHON_GIT_EXECUTABLE']
        elif UTILS.getGitDefault(gitExe):
            return UTILS.getGitDefault(gitExe)
        elif found_git and UTILS.is_exe(found_git):
            return GitHub.install_git(mustAskUser)
        else:
            return ''

    @staticmethod
    def tryPullRepository(repo, user, repository, feedback):
        GitHub.configUser(repo, user)
        try:
            feedback.pushConsoleInfo("Git: Pulling remote repository current state.")
            # UTILS.runLongTask(repo.git.pull, feedback, 'Pease wait, pulling changes.', 30, " -s recursive -X ours " + GitHub.getGitUrl(user, repository) + "master")
            UTILS.runLongTask(repo.git.pull, feedback, 'Pease wait, pulling changes.', 30, "-s", "recursive", "-X", "ours", GitHub.getGitUrl(user, repository), "master")
            feedback.pushConsoleInfo("Before fetch changes.")
            UTILS.runLongTask(repo.git.fetch, feedback, 'Please wait, fetching changes.', 30, GitHub.getGitUrl(user, repository), "master")
            feedback.pushConsoleInfo("Git: Doing checkout.")
            UTILS.runLongTask(repo.git.checkout, feedback, 'Please wait, doing checkout', 30, "--ours")
        except:
            pass

    @staticmethod
    def createRepo(ghRepository, ghUser, ghPass, feedback):
        payload = {
            'name': ghRepository,
            'description': 'Online maps published by Mappia. [List maps in repository](https://maps.csr.ufmg.br/calculator/?map=&queryid=152&listRepository=Repository&storeurl=' + GitHub.getGitUrl(ghUser, ghRepository)+')',
            'homepage': 'https://maps.csr.ufmg.br/calculator/?map=&queryid=152&listRepository=Repository&storeurl=' + GitHub.getGitUrl(ghUser, ghRepository),
            'branch': 'master',
            'auto_init': 'true'
        }
        feedback.pushConsoleInfo("Creating the new repository: " + ghRepository)
        resp = requests.post(GitHub.githubApi + 'user/repos', auth=(ghUser, ghPass), data=json.dumps(payload))
        if resp.status_code == 201:
            sleep(1)
            return True
        else:
            return False

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


    @staticmethod
    def getGitCredentials(curUser, curPass, mustAskUser):
        state = UTILS.randomString()
        if (not curUser):
            curUser = ''
        if (curPass is None or not curPass or not curUser) or (GitHub.testLogin(curUser, curPass) == False and (mustAskUser or QMessageBox.question(
                None, "Credentials required", "Please inform your credentials, could we open login link for you?") == QMessageBox.Yes)):
            url = 'https://github.com/login/oauth/authorize?redirect_uri=https://csr.ufmg.br/imagery/get_key.php&client_id=10b28a388b0e66e87cee&login=' + curUser + '&scope=read:user%20repo&state=' + state
            credentials = {
                'value': None
            }
            GitHub.getCredentials(state)
            webbrowser.open(url, 1)
            isFirstOpen = True
            def checkLoginValidation(btn, timeSpent):
                credentials['value'] = credentials['value'] or GitHub.getCredentials(state)
                if credentials['value'] and not mustAskUser:
                    btn.done(0)
                return True
            while not credentials['value']:
                sleep(1)
                auxMsg = '' if isFirstOpen else '\n\nWaiting validation, re-openning the authorization github page.\nPlease login on a Github account to continue.'
                isFirstOpen = False
                response = CustomMessageBox.showWithCallback(2000,
                      "Click 'YES' to continue or 'NO' to cancel.\nOpenning the github authentication link in browser." + auxMsg,
                      "Please confirm credentials at Github site to continue", checkLoginValidation, buttons=QMessageBox.Yes | QMessageBox.No)
                credentials['value'] = credentials['value'] or GitHub.getCredentials(state)
                if response == QMessageBox.Yes and not credentials['value']:
                    webbrowser.open(url, 2)
                elif response != QMessageBox.Yes and not credentials['value']:
                    return (None, None)
            return (credentials['value']['user'], credentials['value']['token'])
        return (curUser, curPass)

    @staticmethod
    def addFiles(repo, user, repository, feedback):
        return GitInteractive.addFiles(repo, user, repository, feedback)

    @staticmethod
    def gitCommit(repo, msg, feedback):
        return GitInteractive.gitCommit(repo, msg, feedback)

    @staticmethod
    def pushChanges(repo, user, repository, password, feedback):
        return GitInteractive.pushChanges(repo, user, repository, password, feedback)

    @staticmethod
    def publishTilesToGitHub(folder, user, repository, feedback, version, password=None):
        feedback.pushConsoleInfo('Github found commiting to your account.')

        repo = GitHub.getRepository(folder, user, repository, password, feedback)

        now = datetime.now()
        # https://stackoverflow.com/questions/6565357/git-push-requires-username-and-password
        repo.git.config("credential.helper", " ", "store")
        GitHub.tryPullRepository(repo, user, repository, feedback) #Danilo
        feedback.pushConsoleInfo('Git: Add all generated tiles to your repository.')
        GitHub.addFiles(repo, user, repository, feedback)
        #feedback.pushConsoleInfo("Git: Mergin.")
        #repo.git.merge("-s recursive", "-X ours")
        #feedback.pushConsoleInfo("Git: Pushing changes.")
        #repo.git.push(GitHub.getGitUrl(user, repository), "master:refs/heads/master")
        if repo.index.diff(None) or repo.untracked_files:
            feedback.pushConsoleInfo("No changes, nothing to commit.")
            return None
        feedback.pushConsoleInfo("Git: Committing changes.")
        GitHub.gitCommit(repo, "QGIS - " + now.strftime("%d/%m/%Y %H:%M:%S") + " version: " + version, feedback)
        # feedback.pushConsoleInfo("CREATING TAG")
        # tag = now.strftime("%Y%m%d-%H%M%S")
        # new_tag = repo.create_tag(tag, message='Automatic tag "{0}"'.format(tag))
        # repo.remotes[originName].push(new_tag)
        feedback.pushConsoleInfo("Git: Pushing modifications to remote repository.")
        GitHub.pushChanges(repo, user, repository, password, feedback)
        return None

    @staticmethod
    def getCredentials(secret):
        #Danilo #FIXME colocar UNIQUE no BD
        resp = requests.get('https://csr.ufmg.br/imagery/verify_key.php?state=' + secret)
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            return None

    # @staticmethod
    # def getAccessToken(curUser, curPass):
    #     def isNotToken(content):
    #         return not re.match(r'^[a-z0-9]{40}$', content)
    #     # def createTokenFromPass(user, password):
    #     #     params = {
    #     #         "scopes": ["repo", "write:org"],
    #     #         "note": "Mappia Access (" + str(random.uniform(0, 1) * 100000) + ")"
    #     #     }
    #     #     resp = requests.post(url=GitHub.githubApi + 'authorizations', headers={'content-type': 'application/json'}, auth=(user, password), data=json.dumps(params))
    #     #     if resp.status_code == HTTPStatus.CREATED:
    #     #         return json.loads(resp.text)["token"]
    #     #     elif resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
    #     #         #deveria tentar mais uma vez
    #     #         return None
    #     #     elif resp.status_code == HTTPStatus.UNAUTHORIZED:
    #     #         QMessageBox.warning(None, "Mappia Publisher Error", "Failed to login, please check if the entered username/password is valid at (https://github.com/login)")
    #     #         raise Exception("Error: Failed to login, please Verify the entered username/password.")
    #     #     else:
    #     #         QMessageBox.warning(None, "Mappia Publisher Error", "Failed to create a new token. Response code: " + str(resp.status_code) + " Content: " + str(resp.text))
    #     #         raise Exception("Error: Failed to create token. Response code: " + str(resp.status_code) + " Content: " + str(resp.text))
    #     foundToken = None
    #     if not GitHub.testLogin(curUser, curPass):
    #         QMessageBox.warning(None, "Mappia Publisher Error",
    #                             "Failed to login, please check if the entered username/password is valid at (https://github.com/login)")
    #         Exception("Error: Failed to login.")
    #         foundToken = None
    #     elif not isNotToken(curPass) and GitHub.testLogin(curUser, curPass):
    #         foundToken = curPass
    #     elif GitHub.personal_token and not isNotToken(GitHub.personal_token) and GitHub.testLogin(curUser, GitHub.personal_token):
    #         foundToken = GitHub.personal_token
    #     # elif QMessageBox.question(None, "Key required instead of password.", "Want the mappia to automatically create a key for you? Otherwise please access the link: https://github.com/settings/tokens to create the key.", defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
    #     #     retries = 1
    #     #     token = None
    #     #     while token is None and retries <= 5:
    #     #         token = createTokenFromPass(curUser, curPass)
    #     #         retries = retries + 1
    #     #     if token is None:
    #     #         if QMessageBox.question(None, "The token creation have failed. Want to open the creation link?", defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
    #     #             webbrowser.open_new('https://github.com/settings/tokens')
    #     #         raise Exception("Error: Something goes wrong creating the token. Opening the browser, please create your token manually at https://github.com/settings/tokens and enable enable the scope group 'repo'. Please copy the resulting text.")
    #     #     GitHub.personal_token = token
    #     #     QMessageBox.warning(None, "Information", "Created the following token, please copy it to use later '" + token + "'.")
    #     #     foundToken = token
    #     else:
    #         foundToken = None
    #     return foundToken


    @staticmethod
    def _request(*args, **kwargs):
        with_auth = kwargs.pop("with_auth", True)
        token = kwargs.pop("token", '')
        if not token:
            token = os.environ.get("GITHUB_TOKEN", None)
        if token and with_auth:
            kwargs["auth"] = (token, 'x-oauth-basic')
        for _ in range(3):
            response = request(*args, **kwargs)
            is_travis = os.getenv("TRAVIS", None) is not None
            if is_travis and 400 <= response.status_code < 500:
                print("Retrying in 1s (%s Client Error: %s for url: %s)" % (
                    response.status_code, response.reason, response.url))
                time.sleep(1)
                continue
            break
        return response

    @staticmethod
    def _recursive_gh_get(href, items, password=None):
        """Recursively get list of GitHub objects.

        See https://developer.github.com/v3/guides/traversing-with-pagination/
        """
        response = GitHub._request('GET', href, token=password)
        response.raise_for_status()
        items.extend(response.json())
        if "link" not in response.headers:
            return
        # links = link_header.parse(response.headers["link"])
        # rels = {link.rel: link.href for link in links.links}
        # if "next" in rels:
        #     ghRelease._recursive_gh_get(rels["next"], items)

    #Return a list of assets in commit 'releaseName' within this repository.
    @staticmethod
    def getAssets(user, repository, password, tagName):
        release = GitHub.getRelease(user, repository, password, tagName)
        if not release:
            raise Exception('Release with tag_name {0} not found'.format(tagName))
        assets = []
        GitHub._recursive_gh_get(GitHub.githubApi + 'repos/{0}/releases/{1}/assets'.format(
            user + "/" + repository, release["id"]), assets, password)
        return assets

    #If exists get the release with name 'releaseName'.
    @staticmethod
    def getRelease(user, repository, password, tagName):
        def _getRelease(href, password, tagName):
            releaseResp = GitHub._request('GET', href, token=password)
            releaseResp.raise_for_status()
            result = None
            for curResp in releaseResp.json():
                if (curResp and (curResp['tag_name'] == tagName)):
                    result = curResp
                    break
            if result is None and 'link' in releaseResp.headers:
                raise Exception("Please report: not implemented yet." + json.dumps(releaseResp.headers["link"]))
        # if 'link' in releaseResp.headers: #Danilo precisa implementar ainda
        #add resp to curResp.
        #     # links = link_header.parse(response.headers["link"])
        #     # rels = {link.rel: link.href for link in links.links}
        #     # if "next" in rels:
        #     #     ghRelease._recursive_gh_get(rels["next"], items, token)
        #     # Danilo preciso fazer o parse
            return result
        return _getRelease(GitHub.githubApi + 'repos/' + user + "/" + repository + "/releases", password, tagName)

    #Create the download tag or report a error.
    @staticmethod
    def createDownloadTag(user, repository, password, feedback):
        data = {
            'tag_name': GitHub.releaseName,
            'name': GitHub.releaseName,
            'body': GitHub.releaseName,
            'draft': False,
            'prerelease': False
        }
        response = GitHub._request('POST', GitHub.githubApi + 'repos/' + user + "/" + repository + "/releases", token=password, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if (response.status_code == 422) and GitHub.getRelease(user, repository, password, GitHub.releaseName) is not None: #vou considerar q ja está criado
            pass
        else:
            response.raise_for_status()

    #Try to add the 'uploadFile' as a layer asset.
    @staticmethod
    def addReleaseFile(user, password, repository, maxRetry, forceUpdateFile, uploadFile, layer, feedback):
        if uploadFile is None:
            return None
        releaseRef = GitHub.getRelease(user, repository, password, GitHub.releaseName)

        if releaseRef is None or releaseRef['upload_url'] is None:
            raise Exception("Release '" + GitHub.releaseName + "' was not found")
        assets = GitHub.getAssets(user, repository, password, GitHub.releaseName)
        uploadUrl = releaseRef['upload_url']
        if "{" in uploadUrl:
            uploadUrl = uploadUrl[:uploadUrl.index("{")]
        basename = UTILS.normalizeName(os.path.basename(layer.name())) + str(os.path.splitext(uploadFile)[1])
        #Example: #'https://github.com/asfixia/Mappia_Example_t/releases/download/Map_Download/distance_to_deforested.tif'
        fileDownloadPath = 'https://github.com/' + user + "/" + repository + "/releases/download/" + GitHub.releaseName + "/" + basename

        for asset in assets:
            if asset["name"] == basename:
                # See https://developer.github.com/v3/repos/releases/#response-for-upstream-failure  # noqa: E501
                if asset["state"] == "new" or asset["state"] == "uploaded": #override the old file if last upload failed or update if 'forceUpdateFile' is true.
                    if asset["state"] == "uploaded" and not forceUpdateFile:
                        feedback.setProgressText("File %s already uploaded." % asset['name'])
                        return fileDownloadPath
                    if asset["state"] == "new":
                        feedback.setProgressText("  deleting %s (invalid asset "
                              "with state set to 'new')" % asset['name'])
                    else:
                        feedback.setProgressText("Updating file %s." % asset['name'])
                    url = (
                            GitHub.githubApi
                            + 'repos/{0}/releases/assets/{1}'.format(user + "/" + repository, asset['id'])
                    )
                    response = GitHub._request('DELETE', url, token=password)
                    response.raise_for_status()

        file_size = os.path.getsize(uploadFile)
        feedback.setProgressText("  Uploading %s of size %s (MB)" % (basename, str(file_size / 10e5)))

        url = '{0}?name={1}'.format(uploadUrl, basename)

        # Attempt upload
        with open(uploadFile, 'rb') as f:
            with progress_reporter_cls(
                    label=basename, length=file_size, feedback=feedback) as reporter:
                response = GitHub._request(
                    'POST', url, headers={'Content-Type': 'application/octet-stream'},
                    data=_ProgressFileReader(f, reporter), token=password)
                data = response.json()

        if response.status_code == 502 and maxRetry > 1:
            feedback.setProgressText("Retrying (upload failed with status_code=502)")
            return GitHub.addReleaseFile(user, password, repository, maxRetry - 1, forceUpdateFile, uploadFile, layer, feedback)
        elif response.status_code == 502 and maxRetry <= 1:
            return None
        else:
            response.raise_for_status()
        return fileDownloadPath

####################################### AUX CLASS ##########################

class progress_reporter_cls(object):
    reportProgress = False

    def __init__(self, label='', length=0, feedback=None):
        self.label = label
        self.length = length
        self.total = 0
        self.lastReport = 0
        self.feedback = feedback

    def update(self, chunk_size):
        self.total = self.total + chunk_size
        if self.feedback is not None and self.total > (self.lastReport + (self.length * 0.1)):
            self.feedback.setProgressText('Total: ' + str(self.total / 1000) + " (kb)")
            self.lastReport = self.total
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

#Wrapper used to capture File IO read progress.
class _ProgressFileReader(object):
    def __init__(self, stream, reporter):
        self._stream = stream
        self._reporter = reporter

    def read(self, _size):
        _chunk = self._stream.read(_size)
        self._reporter.update(len(_chunk))
        return _chunk

    def __getattr__(self, attr):
        return getattr(self._stream, attr)

class CustomMessageBox(QMessageBox):
    def __init__(self, *__args):
        QMessageBox.__init__(self)
        self.timeout = 0
        self.callback = None
        self.currentTime = 0

    def showEvent(self, QShowEvent):
        self.currentTime = 0
        if self.autoclose:
            self.startTimer(self.timeout)

    def timerEvent(self, event):
        # try:
        if self.isHidden():
            self.killTimer(event.timerId())
            self.deleteLayer()
        else:
            self.currentTime += 1
            self.callback(self, self.currentTime)
        # except:
        #     self.quit()
        # if self.currentTime >= self.timeout:
        #     self.done(0)

    @staticmethod
    def showWithCallback(timeoutMsCallback, message, title, callback, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
        w = CustomMessageBox()
        w.autoclose = True
        w.callback = callback
        w.timeout = timeoutMsCallback
        w.setText(message)
        w.setWindowTitle(title)
        w.setIcon(icon)
        w.setStandardButtons(buttons)
        w.exec_()

class GitInteractive() :

    @staticmethod
    def cloneRepo(user, repository, folder, feedback):
        from git import Repo
        return UTILS.runLongTask(Repo.clone_from, feedback, waitMessage="Please wait to complete the download.",
                                   secondsReport=15, url=GitHub.getGitUrl(user, repository), to_path=folder,
                                   recursive=True)

    @staticmethod
    def pushChanges(repo, user, repository, password, feedback):
        return UTILS.runLongTask(repo.git.push, feedback, 'Please wait, uploading changes.', 30,
                                          GitHub.getGitPassUrl(user, repository, password), "master:refs/heads/master")

    @staticmethod
    def gitCommit(repo, msg, feedback):
        return UTILS.runLongTask(repo.git.commit, feedback, 'Please wait, uploading changes.', 30, m=msg)

    @staticmethod
    def addFiles(repo, user, repository, feedback):
        originName = "mappia"
        try:
            repo.git.remote("add", originName, GitHub.getGitUrl(user, repository))
        except:
            repo.git.remote("set-url", originName, GitHub.getGitUrl(user, repository))
        return UTILS.runLongTask(repo.git.add, feedback, waitMessage='Please wait, identifying changes on your repository.', secondsReport=30, all=True) # Adiciona todos arquivos