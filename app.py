from flask import Flask, render_template
import requests
from flask import jsonify, make_response
from flask import request, send_file
import urllib3, zipfile, hashlib, os, time
import xmltodict
import requests_cache
import pymongo
import os

app = Flask(__name__)

# some links for jenkins
URL_METADATA = "https://repo.codemc.io/repository/maven-releases/world/bentobox/{module}/maven-metadata.xml"
URL_VERSION_INFO = "https://repo.codemc.io/repository/maven-releases/world/bentobox/{module}/{version}/{module}-{version}.pom"
URL_JAR_DOWNLOAD = "https://repo.codemc.io/repository/maven-releases/world/bentobox/{module}/{version}/{module}-{version}.jar"

# bentobox static addon list
BENTOBOX_ADDONS = ["bskyblock", "acidisland", "caveblock", "skygrid", "challenges", "level", "magiccobblestonegenerator", "warps", "likes", "biomes", "voidportals", "IslandFly", "controlpanel", "dimensionaltrees"]

CACHE_FILE_SECONDS = 60*10

requests_cache.install_cache('nexus_cache', backend='sqlite', expire_after=CACHE_FILE_SECONDS)

mongodb = pymongo.MongoClient(os.environ["MONGODB_URI"])["bmj0hz1bfryjijw"]

@app.route('/')
def index():
  return render_template('index.html', addons=dict(map(lambda e: (e["artifactId"], e["version"]), get_valid_addons())))

@app.route('/custom')
def custom():
  return render_template('custom.html', addons=get_valid_addons())

@app.route('/create-jar/')
def create_jar():
  addons = list(map(lambda e: {"artifactId": e.split(":")[0], "version": e.split(":")[1]}, request.args))
  
  for addon in addons:
    increment_stats(addon["artifactId"])

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
    downloadUrl = URL_JAR_DOWNLOAD.format(module=module["artifactId"], version=module["version"])
    return {"fileName": module["artifactId"] + "-" + module["version"] + ".jar", "url": downloadUrl}

urlPoolLib = urllib3.PoolManager()

def getModuleCheksum(modules):
  return hashlib.md5(str(modules).encode('utf-8')).hexdigest()

def getZipFilePath(modules):
  return "zips/bentobox-" + getModuleCheksum(modules) + ".zip"

def buildZip(includingJars):
  downloadLinks = getDownloadLinks(includingJars)

  if not os.path.exists("zips"):
      os.makedirs("zips")
  zf = zipfile.ZipFile(getZipFilePath(includingJars), "w")

  for downloadLink in downloadLinks:
    resp = urlPoolLib.request('GET', downloadLink["url"])
    zf.writestr("BentoBox/addons/" + downloadLink["fileName"], resp.data)
    resp.release_conn()

  xml_dict = get_xmldict_fromurl(URL_METADATA.format(module="bentobox"))
  version = xml_dict["metadata"]["versioning"]["release"]

  downloadLinkBentobox = getDownloadLink({"artifactId": "bentobox", "version": version})

  resp = urlPoolLib.request('GET', downloadLinkBentobox["url"])
  zf.writestr(downloadLinkBentobox["fileName"], resp.data)
  resp.release_conn()
  zf.write("setup_instructions.txt")

def get_valid_addons():
  addons = []
  for artifact_name in BENTOBOX_ADDONS:
    xml_dict = get_xmldict_fromurl(URL_METADATA.format(module=artifact_name))
    version = xml_dict["metadata"]["versioning"]["release"]
    xml_dict2 = get_xmldict_fromurl(URL_VERSION_INFO.format(module=artifact_name, version=version))
    name = xml_dict2["project"]["name"]
    addons.append({"name": name, "version": version, "artifactId": artifact_name, "downloads": format(get_stats(artifact_name))})
  return addons

cached_requests = dict()

def get_xmldict_fromurl(url):
  if url in cached_requests:
    if time.time() - cached_requests[url]["timestamp"] < CACHE_FILE_SECONDS:
      return cached_requests[url]["xml_dict"]
    
  raw_content = urlPoolLib.request('GET', url).data
  xml_dict = xmltodict.parse(raw_content)
  cached_requests[url] = {"timestamp": time.time(), "xml_dict": xml_dict}
  return xml_dict


stats_col = mongodb["stats"]

def get_stats(key):
  document = stats_col.find_one({"_id": key})
  if document:
    return document["val"]
  return 0

def increment_stats(key):
  document = stats_col.find_one({"_id": key})
  if document:
    stats_col.update_one({"_id": key}, {"$inc": {"val": 1}})
  else:
    stats_col.insert_one({"_id": key, "val": 1})

def format(number):
  if number > 1000 and number < 10000:
    return str(round(number / 1000, 1)) + "k"
  elif number >= 10000:
    return str(round(number / 1000, 0)) + "k"
  return number