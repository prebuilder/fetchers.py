import typing
import datetime
import sys
from pathlib import Path, PurePath
from re import Pattern

from ..DownloadTarget import DownloadTarget
from ..FetchConfig import FetchConfig
from ..utils.idded import re2ID
from ..webServices import GitHubService
from . import Discovered, Discoverer


class GitHubReleasesDiscoverer(Discoverer):
	__slots__ = ("repo", "titleRx", "tagRx", "downloadFileNamesRxs", "targetSelector")

	marker = "GitHub"

	@property
	def idComponents(self):
		return (self.repo, re2ID(self.tagRx) if self.tagRx else "", re2ID(self.titleRx) if self.titleRx else "", ",".join(((k + ":" + re2ID(v)) for k, v in sorted(self.downloadFileNamesRxs.items(), key=lambda x: x[0]))), self.targetSelector.__name__)

	def __init__(self, repo: str, tagRx: Pattern, downloadFileNamesRxs: typing.Mapping, titleRx: None = None, targetSelector: None = None) -> None:
		self.repo = repo
		self.tagRx = tagRx
		self.titleRx = titleRx
		self.downloadFileNamesRxs = downloadFileNamesRxs
		if targetSelector is None:
			targetSelector = max
		self.targetSelector = targetSelector

	def __call__(self, fetchConfig: FetchConfig) -> Discovered:
		gh = GitHubService(*self.repo.split("/"))
		tgts = list(gh.getTargets(self.titleRx, self.tagRx, self.downloadFileNamesRxs))

		#ic(tgts)

		selectedTarget = self.targetSelector(tgts)

		print("Selected release:", selectedTarget, file=sys.stderr)
		yield Discovered(selectedTarget.version, {k: DownloadTarget(v.role, v.name, v.uri, max(v.created, v.modified)) for k, v in selectedTarget.files.items()})
