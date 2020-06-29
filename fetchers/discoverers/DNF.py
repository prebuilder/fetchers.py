import datetime
import gzip
import sys
import typing
from pathlib import Path, PurePath
from re import Pattern

import libdnf
import librepo

#import defusedxml.lxml
#import defusedxml.ElementTree
import lxml.etree
import pantarei
import repomd

from ..DownloadTarget import DownloadTarget
from ..FetchConfig import FetchConfig
from ..utils.integrity import sumStringToASCII
from . import Discovered, Discoverer

#xmlParser = defusedxml.ElementTree.parse  # more secure, but slower
xmlParser = lxml.etree.parse  # lot faster


class DNFDiscoverer(Discoverer):
	__slots__ = ("repoURI", "packages", "gpgKeys", "librepoHandle", "metalinkURI")

	marker = "DNF"

	@property
	def idComponents(self):
		return (self.repoURI if self.repoURI else self.metalinkURI, str(self.gpgKeys), ",".join(self.packages))

	def __init__(self, packages: typing.Iterable[str], gpgKeys, repoURI: str = None, metalinkURI=None) -> None:
		self.repoURI = repoURI  # "https://download.opensuse.org/distribution/openSUSE-current/repo/oss/", "https://sjc.edge.kernel.org/fedora-buffet/fedora/linux/development/rawhide/Everything/x86_64/os/", "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/"
		self.metalinkURI = metalinkURI  # "https://mirrors.fedoraproject.org/metalink?repo=rawhide&arch="+basearch
		if repoURI is None is metalinkURI is None:
			raise ValueError("You must choose either `metalinkURI` or `repoURI`")

		if not gpgKeys:
			warnings.warn("repomd.xml is not verified! The only barriers between you and adversary are both TLS security and infrastructure security.")
			if metalinkURI is not None and not metalinkURI.startswith("https://"):
				raise Exception("`metalinkURI` may be insecure, aborting.")
			if repoURI is not None and not repoURI.startswith("https://"):
				raise Exception("`repoURI` may be insecure, aborting.")

		self.packages = packages
		if isinstance(gpgKeys, Path):
			gpgKeys = (gpgKeys,)

		self.gpgKeys = gpgKeys

		self.librepoHandle = librepo.Handle()
		self.librepoHandle.repotype = librepo.RPMMDREPO
		self.librepoHandle.gpgcheck = True
		self.librepoHandle.sslverifypeer = True
		self.librepoHandle.metalinkurl = None
		self.librepoHandle.yumdlist = ["primary"]

	def __call__(self, fetchConfig: FetchConfig) -> Discovered:
		targetDir = fetchConfig.downloadsTmp / ("librepo_" + sumStringToASCII(repr(self.metalinkURI) + "_" + repr(self.repoURI)))
		targetDir.mkdir(parents=True, exist_ok=True)

		if (targetDir / "repodata" / "repomd.xml").is_file():
			self.librepoHandle.local = True
			self.librepoHandle.urls = [str(targetDir)]
		else:
			self.librepoHandle.local = False
			if self.metalinkURI is not None:
				#self.librepoHandle.fetchmirrors = True
				#self.librepoHandle.metalinkurl = self.metalinkURI
				raise NotImplementedError("ToDo: shit, it seemingly uses http without tls, we will deal with metalinks ourselves")
			else:
				self.librepoHandle.urls = [self.repoURI]

		# self.librepoHandle.local = True

		self.librepoHandle.destdir = str(targetDir)

		if self.gpgKeys:
			from OpenPGPAbs.gpgBackends.gpgme import GPGMe

			gpgmeBackend = GPGMe(gpgme_home=fetchConfig.gpgme_home)
			fetchConfig.gpgme_home.mkdir(parents=True, exist_ok=True)
			self.librepoHandle.gnupghomedir = str(fetchConfig.gpgme_home)
			for k in self.gpgKeys:
				for k in gpgmeBackend.importKey(k):
					issues = gpgmeBackend.isConsideredInsecure(k)
					if issues:
						raise Exception("Key is considered insecure", k)

		r = librepo.Result()

		pb = None
		prevTotal = None
		prevDownloaded = None

		def callback(data, total, downloaded):
			nonlocal pb, prevDownloaded, prevTotal
			print(data, total, downloaded)
			if total != downloaded.total or prevDownloaded > downloaded or downloaded == 0:
				if pb is not None:
					pb.__exit__(None, None, None)
					pb = None

			if pb is None:
				prevTotal = total
				pb = fetchConfig.progressReporter(total, title="aaa")
				pb = pb.__enter__()
			else:
				pb.report(
					data,
					progress=downloaded,
					op="Fetching from repo",
				)
				prevDownloaded = downloaded

		self.librepoHandle.perform(r)
		if pb is not None:
			pb.__exit__(None, None, None)

		r.getinfo(librepo.LRR_RPMMD_REPO)
		info = r.getinfo(librepo.LRR_RPMMD_REPOMD)
		recs = info["records"]

		print("Parsing repomd.xml...")
		with gzip.open(str(targetDir / recs["primary"]["location_href"]), "rt", encoding="utf-8") as f:
			md = xmlParser(f)
		r = repomd.Repo(self.repoURI, md)

		with fetchConfig.progressReporter(len(self.packages), title="Searching packages in metadata") as pb:
			i = 0
			for pkgName in self.packages:
				pb.report(pkgName, progress=i)
				pkg = r.find(pkgName)
				i += 1
				pb.report(pkgName, progress=i)
				if pkg:
					yield Discovered(pkg.version, {"binary.rpm": DownloadTarget("binary.rpm", pkg.name, r.baseurl + pkg.location, pkg.build_time)})
				else:
					raise KeyError("Package `" + pkgName + "` hasn't been found in `" + r.baseurl + "`")
