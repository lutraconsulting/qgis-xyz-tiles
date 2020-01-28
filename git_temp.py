from git_temp import Repo
import os
from datetime import datetime

ghPath = "C:\\Export\\Trampo\\modelos\\GitHubWMS\\WMS4\\"
#os.chdir(ghPath)
#if not os.path.isfile(os.environ['GIT_SSH']):
#    raise Exception(
#        f'Missing custom SSH script {os.environ["GIT_SSH"]}!\n\n'
#        'You must provide a custom SSH script which can be able to execute git commands with the correct SSH key.\n'
#        'The bash script should contain this line:\n\n'
#        'ssh -i <SSH_private_key> -oIdentitiesOnly=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "$@"\n\n'
#    )

username = "asfixia"
passphrase = ""
ghRepository = "CustomWMS"

#GIT_PYTHON_GIT_EXECUTABLE

#Precisa adicionar o SSH key antes de rodar.
if not os.path.exists(ghPath):
    os.mkdir(ghPath)
    repo = Repo.init(ghPath, bare=True)
else:
    repo = Repo(ghPath)

if repo.bare:
    repo.git.clone(f'https://{username}:{passphrase}@github.com/{username}/{ghRepository}.git "{ghPath}"')
repo.git.add(all=True) #Adiciona todos arquivos
now = datetime.now()
if repo.is_dirty():
    tag = "v:" + now.strftime("%Y%m%d-%H%M%S")
    new_tag = repo.create_tag(tag, message='Automatic tag "{0}"'.format(tag))
    repo.remotes.origin.push(new_tag)

repo.git.commit(m="QGIS - " + now.strftime("%d/%m/%Y %H:%M:%S"))
repo.git.pull("origin", "master")
repo.git.checkout()
repo.git.push()


install("gitpython")
from git import Repo

# ghPath = "C:\\Export\\Trampo\\modelos\\GitHubWMS\\WMS4\\"
# username = "asfixia"
# passphrase = ""
# ghRepository = "CustomWMS"

# GIT_PYTHON_GIT_EXECUTABLE
ghPath = "C:\\Export\\Trampo\\modelos\\GitHubWMS\\WMS4\\"#self.folder
# Precisa adicionar o SSH key antes de rodar.
if not os.path.exists(ghPath):
    os.mkdir(ghPath)
    repo = Repo.init(ghPath, bare=True)
else:
    repo = Repo(ghPath)

# if repo.bare:
#    repo.git.clone(f'https://{username}:{passphrase}@github.com/{username}/{ghRepository}.git "{ghPath}"')
repo.git.add(all=True)  # Adiciona todos arquivos
now = datetime.now()
if repo.is_dirty():
    tag = "v:" + now.strftime("%Y%m%d-%H%M%S")
    new_tag = repo.create_tag(tag, message='Automatic tag "{0}"'.format(tag))
    repo.remotes.origin.push(new_tag)

repo.git.commit(m="QGIS - " + now.strftime("%d/%m/%Y %H:%M:%S"))
repo.git.pull("origin", "master")
repo.git.checkout()
repo.git.push()