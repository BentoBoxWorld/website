from flask import Flask, render_template
import requests
from flask import jsonify
from flask import request, send_file
import urllib3, zipfile, hashlib, os, time


app = Flask(__name__)

# some links for jenkins
URL_MODULES = "https://ci.codemc.org/job/BentoBoxWorld/api/json"
URL_GET_MODULE = "https://ci.codemc.org/job/BentoBoxWorld/job/{module}/lastSuccessfulBuild/api/json"
URL_ARTIFACT = "https://ci.codemc.org/job/BentoBoxWorld/job/{module}/lastSuccessfulBuild/artifact/target/{filename}"

CACHE_FILE_SECONDS = 60*5

@app.route('/')
def index():
  addon_names = get_addons()
  return render_template('index.html', essentials=addon_names[:2], addons=addon_names[2:])

@app.route('/create-jar/')
def create_jar():
  addons = []
  addons.append(request.args.get('gamemode', None))

  for arg in request.args:
    if arg != "gamemode":
      addons.append(arg)

  # check if the zip is cached for this addons
  zipPath = getZipFilePath(addons)

  if not os.path.exists(zipPath) or time.time() - os.stat(zipPath).st_mtime > CACHE_FILE_SECONDS:
    buildZip(addons)

  print(zipPath)
  return send_file(zipPath, attachment_filename='BentoBox.zip', as_attachment=True)

def getDownloadLinks(modules):
  links = []
  for module in modules:
    links.append(getDownloadLink(module))
  return links

def getDownloadLink(module):
    print(URL_GET_MODULE.format(module=module))
    result = requests.get(URL_GET_MODULE.format(module=module)).json()
    fileName = result["artifacts"][-1]["fileName"]
    return [fileName, URL_ARTIFACT.format(module=module, filename=fileName)]

urlPoolLib = urllib3.PoolManager()

def getModuleCheksum(modules):
  return hashlib.md5("".join(modules).encode('utf-8')).hexdigest()

def getZipFilePath(modules):
  return "zips/bentobox-" + getModuleCheksum(modules) + ".zip"

def buildZip(includingJars):
  downloadLinks = getDownloadLinks(includingJars)

  if not os.path.exists("zips"):
      os.makedirs("zips")
  zf = zipfile.ZipFile(getZipFilePath(includingJars), "w")

  for downloadLink in downloadLinks:
    resp = urlPoolLib.request('GET', downloadLink[1])
    zf.writestr("BentoBox/addons/" + downloadLink[0], resp.data)
    resp.release_conn()

  downloadLinkBentobox = getDownloadLink("bentobox")

  resp = urlPoolLib.request('GET', downloadLinkBentobox[1])
  zf.writestr(downloadLinkBentobox[0], resp.data)
  resp.release_conn()
  zf.write("setup_instructions.txt")


def get_addons():
  r = requests.get(URL_MODULES)
  obj = r.json()
  addon_names = []
  for job in obj["jobs"]:
    if job["name"].startswith("addon") and job["color"] != "red":
      addon_names.append(job["name"])
  return addon_names