import datetime

import requests
from dateutil.parser import parse as parseDT

from ..DownloadTarget import DownloadTarget, DownloadTargetFile
from ..Service import CodeHostingServiceDefaultBranch, ServiceDomainBasedDetector

GH_API_BASE = "https://api.github.com/"


def getLastCommitOnBranchURI(owner, repo, branch="master"):
	return GH_API_BASE + "repos/" + owner + "/" + repo + "/git/ref/heads/" + branch


def getTagsURI(owner, repo):
	return GH_API_BASE + "repos/" + owner + "/" + repo + "/tags"


def GitHubRequest(uri):
	req = requests.get(uri)
	headers = requests.utils.default_headers()
	h = req.headers
	limitRemaining = int(h["X-RateLimit-Remaining"])
	limitTotal = int(h["X-RateLimit-Limit"])
	limitResetTime = datetime.datetime.utcfromtimestamp(int(h["X-RateLimit-Reset"]))

	print(limitRemaining, "/", limitTotal, str((limitRemaining / limitTotal) * 100.0) + "%", "limit will be reset:", limitResetTime, "in", limitResetTime - datetime.datetime.now())
	req.raise_for_status()
	t = req.json()
	#ic(t)

	if isinstance(t, dict) and "message" in t:
		raise Exception(t["message"])
	return t


class GitHubService(ServiceDomainBasedDetector, CodeHostingServiceDefaultBranch):
	domainParts = {("github", "com")}

	@classmethod
	def genArgs(cls, parsedUri):
		s = parsedUri.path.split("/")
		if not (s[0] == "" and len(s) == 3):
			raise ValueError("Incorrect URI for GitHub")
		return dict(zip(("owner", "repo"), s[1:]))

	def getRepoTagsInfo(self):
		return GitHubRequest(getTagsURI(self.owner, self.repo))

	def __init__(self, owner, repo):
		self.owner = owner
		self.repo = repo

	def getTargets(self, titleRx, tagRx, downloadFileNamesRxs, signed=False):
		repoPath = self.owner + "/" + self.repo
		if not isinstance(downloadFileNamesRxs, dict):
			downloadFileNamesRxs = {None: downloadFileNamesRxs}

		RELEASES_EP = GH_API_BASE + "repos/" + repoPath + "/releases"

		t = GitHubRequest(RELEASES_EP)

		for r in t:
			nm = r["name"]
			if titleRx is not None and not titleRx.match(nm):
				continue
			tagMatch = tagRx.match(r["tag_name"])

			if not tagMatch:
				continue

			v = tagMatch.group(1)
			c = parseDT(r["created_at"])
			p = parseDT(r["published_at"])
			files = {}
			for a in r["assets"]:
				for role, downloadFileNameRx in downloadFileNamesRxs.items():
					if not downloadFileNameRx.match(a["name"]):
						continue
					fc = parseDT(a["created_at"])
					m = parseDT(a["updated_at"])
					files[role] = DownloadTargetFile(role, a["name"], fc, m, a["browser_download_url"], a["size"])
			if len(files) == len(downloadFileNamesRxs):
				yield DownloadTarget(nm, v, r["prerelease"], r["draft"], c, p, files)
