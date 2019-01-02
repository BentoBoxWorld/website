from flask import Flask, render_template
import requests
from flask import jsonify, make_response
from flask import request, send_file
import urllib3, zipfile, hashlib, os, time


app = Flask(__name__)

# some links for jenkins
URL_MODULES = "https://ci.codemc.org/job/BentoBoxWorld/api/json"
URL_GET_MODULE = "https://ci.codemc.org/job/BentoBoxWorld/job/{module}/lastSuccessfulBuild/api/json"
URL_ARTIFACT = "https://ci.codemc.org/job/BentoBoxWorld/job/{module}/lastSuccessfulBuild/artifact/target/{filename}"

# bentobox static addon list
BENTOBOX_ADDONS = ["BSkyBlock", "AcidIsland", "Challanges", "Level", "addon-welcomewarpsigns", "addon-invSwitcher", "addon-limits"]

CACHE_FILE_SECONDS = 60*5

@app.route('/')
def index():
  return render_template('index.html', addons=get_valid_addons())

@app.route('/create-jar/')
def create_jar():
  addons = list(map(lambda e: e, request.args))
  
  # check if the zip is cached for this addons
  zipPath = getZipFilePath(addons)

  if not os.path.exists(zipPath) or time.time() - os.stat(zipPath).st_mtime > CACHE_FILE_SECONDS:
    buildZip(addons)
    
  resp = make_response(send_file(zipPath, attachment_filename='BentoBox.zip', as_attachment=True))
  resp.set_cookie('downloaded', '1')
  return resp

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

  downloadLinkBentobox = getDownloadLink("BentoBox")

  resp = urlPoolLib.request('GET', downloadLinkBentobox[1])
  zf.writestr(downloadLinkBentobox[0], resp.data)
  resp.release_conn()
  zf.write("setup_instructions.txt")

def get_valid_addons():
  r = requests.get(URL_MODULES)
  obj = r.json()
  addon_names = []
  for job in obj["jobs"]:
    if job["name"] in BENTOBOX_ADDONS and job["color"] != "red":
      app.logger.debug("job for %s failed", job["name"])
      addon_names.append(job["name"])
  return addon_names