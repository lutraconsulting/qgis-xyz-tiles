from http import HTTPStatus
import re
import os
import random
import webbrowser
import requests
from datetime import datetime
import json
from git import Repo
from git import InvalidGitRepositoryError
from qgis.PyQt.QtWidgets import QMessageBox

class GitHub:

    personal_token = ''

    @staticmethod
    def testLogin(user, token):
        return requests.get(url='https://api.github.com/user', auth=(user, token)).status_code == 200

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
    def getGitExe():
        gitExe = ''
        try:
            gitExe = os.environ['GIT_PYTHON_GIT_EXECUTABLE']
        except:
            pass
        return gitExe

    @staticmethod
    def getGitUrl(githubUser, githubRepository):
        return "https://github.com/" + githubUser + "/" + githubRepository + "/"

    #No password to allow using configured SSHKey.
    @staticmethod
    def getGitPassUrl(user, repository, password):
        if password is None or not password:
            return GitHub.getGitUrl(user, repository)
        return "https://" + user + ":" + password + "@github.com/" + user + "/" + repository + ".git"

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
    def isOptionsOk(folder, user, password, repository, feedback):
        from git import Repo
        from git import InvalidGitRepositoryError

        #feedback.pushConsoleInfo('Github found commiting to your account.')
        # if not GitHub.existsRepository(user, repository):
        #     feedback.pushConsoleInfo("The repository " + repository + " doesn't exists.\nPlease create a new one at https://github.com/new .")
        #     return False

        #Cria ou pega o repositório atual.
        repo = None #Danilo copia ou msma função do  getRepository
        if not os.path.exists(folder) or (os.path.exists(folder) and not os.listdir(folder)):
            repo = Repo.clone_from(GitHub.getGitUrl(user, repository), folder)
            assert (os.path.exists(folder))
        else:
            try:
                repo = Repo(folder)
                repoUrl = repo.git.remote("-v")
                expectedUrl = GitHub.getGitUrl(user, repository)
                if repoUrl and not (expectedUrl in re.compile("[\\n\\t ]").split(repoUrl)):
                    feedback.pushConsoleInfo("Your remote URL " + repoUrl + " does not match the expected url " + expectedUrl)
                    return False
            except InvalidGitRepositoryError:
                feedback.pushConsoleInfo("The destination folder must be a repository or an empty folder.")
                #repo = Repo.init(folder, bare=False)
                return False

        if repo.git.status("--porcelain"):
            # if QMessageBox.question(None, "Local repository is not clean.", "Click 'YES' to commit the changes of your folder, otherwise click 'NO' to resolve it yourself.", defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
            #     feedback.pushConsoleInfo("Adding all files in folder")
            #     GitHub.addFiles(repo, user, repository)
            #     feedback.pushConsoleInfo("Adding all files in folder")
            #     repo.git.commit(m="QGIS - Adding all files in folder " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            #     feedback.pushConsoleInfo("QGIS - Sending changes to Github")
            #     GitHub.pushChanges(repo, user, repository, password)
            # else:
            #Pode usar o | git clean -df | git checkout -- . pra descardar tbm
            feedback.pushConsoleInfo("Error: Local repository is not clean.\nPlease commit the changes made to local repository before run.\nUse: git add * and git commit -m \"MSG\"")
            return False
        return True

    @staticmethod
    def getRepository(folder, user, repository, feedback):


        #Não está funcionando a validação
        #feedback.pushConsoleInfo(user + ' at ' + repository)
        if not GitHub.existsRepository(user, repository):
            feedback.pushConsoleInfo("The repository " + repository + " doesn't exists.\nPlease create a new one at https://github.com/new .")
            return None

        #Cria ou pega o repositório atual.
        repo = None
        if not os.path.exists(folder) or os.path.exists(folder) and not os.listdir(folder):
            repo = Repo.clone_from(GitHub.getGitUrl(user, repository), folder)
            assert (os.path.exists(folder))
        else:
            try:
                repo = Repo(folder)
            except InvalidGitRepositoryError:
                feedback.pushConsoleInfo("The destination folder must be a repository or an empty folder.")
                repo = Repo.init(folder, bare=False)
        return repo

    @staticmethod
    def tryPullRepository(repo, user, repository, feedback):
        try:
            feedback.pushConsoleInfo("Git: Pulling your repository current state.")
            repo.git.pull("-s recursive", "-X ours", GitHub.getGitUrl(user, repository), "master")
            feedback.pushConsoleInfo("Git: Doing checkout.")
            repo.git.fetch(GitHub.getGitUrl(user, repository), "master")
            feedback.pushConsoleInfo("Git: Doing checkout.")
            repo.git.checkout("--ours")
        except:
            pass

    @staticmethod
    def addFiles(repo, user, repository):
        originName = "mappia"
        try:
            repo.git.remote("add", originName, GitHub.getGitUrl(user, repository))
        except:
            repo.git.remote("set-url", originName, GitHub.getGitUrl(user, repository))
        repo.git.add(all=True)  # Adiciona todos arquivos

    @staticmethod
    def pushChanges(repo, user, repository, password):
        return repo.git.push(GitHub.getGitPassUrl(user, repository, password), "master:refs/heads/master")

    @staticmethod
    def publishTilesToGitHub(folder, user, repository, feedback, password=None):  # ghRepository, ghUser, ghPassphrase
        feedback.pushConsoleInfo('Github found commiting to your account.')

        repo = GitHub.getRepository(folder, user, repository, feedback)

        now = datetime.now()
        # https://stackoverflow.com/questions/6565357/git-push-requires-username-and-password
        # repo.git.config("credential.helper", "store")
        # repo.git.config("--global", "credential.helper", "'cache --timeout 7200'")
        GitHub.tryPullRepository(repo, user, repository, feedback)
        # feedback.pushConsoleInfo('Git: Add all generated tiles to your repository.')
        GitHub.addFiles(repo, user, repository)
        #feedback.pushConsoleInfo("Git: Mergin.")
        #repo.git.merge("-s recursive", "-X ours")
        #feedback.pushConsoleInfo("Git: Pushing changes.")
        #repo.git.push(GitHub.getGitUrl(user, repository), "master:refs/heads/master")
        if repo.index.diff(None) or repo.untracked_files:
            feedback.pushConsoleInfo("No changes, nothing to commit.")
        feedback.pushConsoleInfo("Git: Committing changes.")
        repo.git.commit(m="QGIS - " + now.strftime("%d/%m/%Y %H:%M:%S"))
        # feedback.pushConsoleInfo("CREATING TAG")
        # tag = now.strftime("%Y%m%d-%H%M%S")
        # new_tag = repo.create_tag(tag, message='Automatic tag "{0}"'.format(tag))
        # repo.remotes[originName].push(new_tag)
        feedback.pushConsoleInfo("Git: Pushing modifications to remote repository.")
        GitHub.pushChanges(repo, user, repository, password)
        return None

    @staticmethod
    def getCredentials(secret):
        #Danilo #FIXME colocar UNIQUE no BD
        resp = requests.get('https://csr.ufmg.br/imagery/verify_key.php?state=' + secret)
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            return None

    @staticmethod
    def getAccessToken(curUser, curPass):
        def isNotToken(content):
            return not re.match(r'^[a-z0-9]{40}$', content)

        def createTokenFromPass(user, password):
            params = {
                "scopes": ["repo", "write:org"],
                "note": "Mappia Access (" + str(random.uniform(0, 1) * 100000) + ")"
            }
            resp = requests.post(url='https://api.github.com/authorizations', headers={'content-type': 'application/json'}, auth=(user, password), data=json.dumps(params))
            if resp.status_code == HTTPStatus.CREATED:
                return json.loads(resp.text)["token"]
            elif resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                #deveria tentar mais uma vez
                return None
            elif resp.status_code == HTTPStatus.UNAUTHORIZED:
                QMessageBox.warning(None, "Mappia Publisher Error", "Failed to login, please check if the entered username/password is valid at (https://github.com/login)")
                raise Exception("Error: Failed to login, please Verify the entered username/password.")
            else:
                QMessageBox.warning(None, "Mappia Publisher Error", "Failed to create a new token. Response code: " + str(resp.status_code) + " Content: " + str(resp.text))
                raise Exception("Error: Failed to create token. Response code: " + str(resp.status_code) + " Content: " + str(resp.text))

        foundToken = None
        if not GitHub.testLogin(curUser, curPass):
            QMessageBox.warning(None, "Mappia Publisher Error",
                                "Failed to login, please check if the entered username/password is valid at (https://github.com/login)")
            Exception("Error: Failed to login.")
            foundToken = None
        elif not isNotToken(curPass) and GitHub.testLogin(curUser, curPass):
            foundToken = curPass
        elif GitHub.personal_token and not isNotToken(GitHub.personal_token) and GitHub.testLogin(curUser, GitHub.personal_token):
            foundToken = GitHub.personal_token
        elif QMessageBox.question(None, "Key required instead of password.", "Want the mappia to automatically create a key for you? Otherwise please access the link: https://github.com/settings/tokens to create the key.", defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
            retries = 1
            token = None
            while token is None and retries <= 5:
                token = createTokenFromPass(curUser, curPass)
                retries = retries + 1
            if token is None:
                if QMessageBox.question(None, "The token creation have failed. Want to open the creation link?", defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
                    webbrowser.open_new('https://github.com/settings/tokens')
                raise Exception("Error: Something goes wrong creating the token. Opening the browser, please create your token manually at https://github.com/settings/tokens and enable enable the scope group 'repo'. Please copy the resulting text.")
            GitHub.personal_token = token
            QMessageBox.warning(None, "Information", "Created the following token, please copy it to use later '" + token + "'.")
            foundToken = token
        else:
            foundToken = None
        return foundToken