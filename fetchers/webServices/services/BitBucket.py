import requests

from ..Service import CodeHostingServiceDefaultBranch, ServiceDomainBasedDetector

BB_API_BASE = "https://api.bitbucket.org/2.0"


def getTagsURI(owner, repo):
	return GH_API_BASE + "repositories/" + owner + "/" + repo + "/refs/tags"


def BitBucketRequest(uri):
	req = requests.get(uri)
	req.raise_for_status()
	t = req.json()
	return t


class BitBucketService(ServiceDomainBasedDetector, CodeHostingServiceDefaultBranch):
	domainParts = {("bitbucket", "org")}

	@classmethod
	def genArgs(cls, parsedUri):
		s = parsedUri.path.split("/")
		if not (s[0] == "" and len(s) == 3):
			raise ValueError("Incorrect URI for BitBucket")
		return dict(zip(("owner", "repo"), s[1:]))

	def __init__(self, owner, repo):
		self.owner = owner
		self.repo = repo

	def getRepoTagsInfo(self):
		return BitBucketRequest(getTagsURI(self.owner, self.repo))
