from urllib.parse import ParseResult, quote_plus

import requests

from ..Service import CodeHostingServiceDefaultBranch, ServiceDomainBasedDetector

from GitLabInstancesDataset import isGitLab

# https://gitlab.com/dslackw/colored -> dslackw/colored


class GitLabService(ServiceDomainBasedDetector, CodeHostingServiceDefaultBranch):
	domainParts = knownServices["GitLab"]

	@classmethod
	def detect(cls, uri) -> bool:
		return super().detect(uri) or "gitlab" in set(uri.path.split("/"))

	@classmethod
	def _detect(cls, parts) -> ParseResult:
		return "gitlab" in set(parts) or isGitLab(parts)

	@classmethod
	def genArgs(cls, parsedUri):
		s = parsedUri.path.split("/")
		if s[0] != "" or len(s) < 2:
			raise ValueError("Incorrect URI for GitLab", parsedUri)

		p = parsedUri.path[1:]
		getToken = ".git"
		if p.endswith(getToken):
			p = p[: -len(getToken)]
		return {"serviceBase": parsedUri.netloc, "repoPath": p}

	def gitLabRequest(self, uri):
		req = requests.get(uri)
		req.raise_for_status()
		t = req.json()
		if "error" in t:
			raise Exception(t["error"])
		return t

	def getTagsURI(self):
		return self.GL_REST_API_BASE + "/projects/" + quote_plus(self.repoPath) + "/repository/tags"

	def __init__(self, serviceBase, repoPath):
		self.serviceBase = serviceBase
		self.repoPath = repoPath
		self.GL_REST_API_BASE = "https://" + serviceBase + "/api/v4"
		self.GL_GRAPHQL_API_BASE = "https://" + serviceBase + "/api/graphql"

	def getRepoTagsInfo(self):
		return self.gitLabRequest(self.getTagsURI())
