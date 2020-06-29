from pathlib import PurePath
from urllib.parse import urljoin, urlparse, urlunparse

import bs4
import requests
from dateutil.parser import parse as parseDateTime

from ..DownloadTarget import DownloadTarget
from ..FetchConfig import FetchConfig
from ..utils.url import fixHTTPS
from . import Discovered, Discoverer

binaryMultipliers = {
	"E": 1 << 60,
	"P": 1 << 50,
	"T": 1 << 40,
	"G": 1 << 30,
	"M": 1 << 20,
	"K": 1 << 10
}


def ourGet(uri):
	return requests.get(fixHTTPS(uri))


familiesBase = "https://download.qt.io/official_releases/qt/"


class MirrorBrainzReleasesDiscoverer(Discoverer):
	__slots__ = ("familiesBase", "platform")

	marker = "MBZ"

	@property
	def idComponents(self):
		return (self.familiesBase, self.platform)

	def __init__(self, familiesBase: str = familiesBase, platform="win32") -> None:
		self.familiesBase = familiesBase
		self.platform = platform

	def parseMirrorBrainDir(self, uri):
		res = ourGet(uri)
		s = bs4.BeautifulSoup(res.text, "lxml")
		tbl = s.select_one("table")
		header = []
		res = []
		for r in tbl.select("tr"):
			if not header:
				for c in r.select("th"):
					header.append(c.text.strip().lower())
			else:
				rowRes = []
				for c in r.select("td"):
					t = c.text.strip()
					hr = c.select_one("a")
					if hr:
						ur = hr.attrs["href"]
					else:
						ur = None
					rowRes.append([t, ur])

				rec = dict(zip(header, rowRes))
				if rec:
					if rec["size"][0] != "-":
						multiplier = 1
						if rec["size"][0][-1] in binaryMultipliers:
							multiplier = binaryMultipliers[rec["size"][0][-1]]
							rec["size"][0] = rec["size"][0][:-1]
						rec["size"][0] = float(rec["size"][0]) * multiplier
					else:
						rec["size"][0] = None

					if rec["last modified"][0]:
						rec["last modified"][0] = parseDateTime(rec["last modified"][0])
					else:
						continue

					if rec["name"][0]:
						rec["dir"] = rec["name"][0][-1] == "/"
						rec["name"][0] = rec["name"][0].strip("/")

					res.append(rec)
		return res

	def parseVersionsDir(self, uri):
		vers = self.parseMirrorBrainDir(uri)
		for verDescr in vers:
			verDescr["version"] = tuple(int(vn) for vn in verDescr["name"][0].split("."))
		return vers

	def __call__(self, fetchConfig: FetchConfig) -> Discovered:
		raise NotImplementedError("Not yet implemented")

		uris = self.getQtInstallerMetadataFilesURIs()
		meta4Text = ourGet(uris["meta4"]).text
		meta4XML = bs4.BeautifulSoup(meta4Text, "xml")
		fEl = meta4XML.select_one("file")
		urisEls = list(fEl.select("url"))
		for u in urisEls:
			u.string = fixHTTPS(u.string)
		if not fEl.select("metaurl[mediatype=torrent]"):
			t = bs4.Tag(name="metaurl")
			t.attrs["mediatype"] = "torrent"
			t.string = uris["torrent"]
			urisEls[0].insert_before(t)

		magnetUri = ourGet(uris["magnet"]).text.strip()

		t = bs4.Tag(name="url")
		t.attrs["priority"] = "0"
		t.string = magnetUri
		urisEls[0].insert_before(t)
		return meta4XML

		yield Discovered(selectedTarget.version, {k: DownloadTarget(v.role, v.name, v.uri, max(v.created, v.modified)) for k, v in selectedTarget.files.items()})

	def getQtInstallersMirrorListURIs(self):
		families = self.parseVersionsDir(familiesBase)
		latestFamily = max(families, key=lambda f: f["version"][0])

		latestFamilyURI = urljoin(familiesBase, latestFamily["name"][1])
		versions = self.parseVersionsDir(latestFamilyURI)
		latestVersion = max(versions, key=lambda f: f["version"][0])

		filesURI = urljoin(latestFamilyURI, latestVersion["name"][1])
		files = self.parseMirrorBrainDir(filesURI)

		installersSuffixesPlatformMap = {"exe": "win32", "dmg": "mac", "run": "linux"}

		res = {}
		for f in files:
			if f["metadata"]:
				fn = PurePath(f["name"][0])
				if fn.suffix:
					s = fn.suffix[1:]
					if s in installersSuffixesPlatformMap:
						res[installersSuffixesPlatformMap[s]] = urljoin(filesURI, f["metadata"][1])

		return res

	def getQtInstallerMetadataFilesURIs(self):
		installerMetaLink = getQtInstallersMirrorListURIs()[self.platform]

		res = ourGet(installerMetaLink)
		s = bs4.BeautifulSoup(res.text, "lxml")
		interestedExtensions = {"meta4", "torrent", "magnet", "sha256"}
		res = {}
		for l in s.select("a"):
			pl = urlparse(l["href"])
			fn = PurePath(pl.path)
			if fn.suffix:
				s = fn.suffix.lower()[1:]
				if s in interestedExtensions:
					res[s] = fixHTTPS(pl)
		return res
