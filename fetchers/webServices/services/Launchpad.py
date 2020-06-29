import requests

from ..Service import CodeHostingServiceDefaultBranch, ServiceDomainBasedDetector

LP_REST_API_BASE = "https://api.launchpad.net/devel"


# https://git.launchpad.net/~pythoneers/+git/distlib


def getRepoInfoURI(owner, project, repo=None, vcs="git"):
	if repo is None:
		repo = project
		project = None
	return LP_REST_API_BASE + "/~" + owner + ("/" + project if project else "") + "/+" + vcs + "/" + repo


def LaunchpadRequest(uri):
	req = requests.get(uri, headers={"Accept": "application/json"})
	req.raise_for_status()
	t = req.json()
	if "error" in t:
		raise Exception(t["error"])
	return t


class LaunchpadService(ServiceDomainBasedDetector, CodeHostingServiceDefaultBranch):
	domainParts = {("git", "launchpad", "net"), ("bzr", "launchpad", "net")}

	def __init__(self, owner, project, repo=None, vcs="git"):
		self.owner = owner
		self.project = project
		self.repo = repo

	def getRepoInfo(self, project, repo=None, vcs="git"):
		return LaunchpadRequest(getRepoInfoURI(self.owner, self.project, repo=self.repo, vcs=self.vcs))

	@classmethod
	def genArgs(cls, parsedUri):
		p = parsedUri.path.split("/")
		if p[0] != "":
			raise ValueError("Incorrect URI for Launchpad")

		owner = p[1]
		vcs = p[2]
		repoName = p[3]
		if owner[0] != "~":
			raise ValueError("owner name in URI must begin from ~")
		owner = owner[1:]

		if vcs[0] != "+":
			raise ValueError("vcs name in URI must begin from +")
		vcs = vcs[1:]

		project = None  # TODO!

		return {"owner": owner, "project": project, "repo": repoName, "vcs": vcs}
