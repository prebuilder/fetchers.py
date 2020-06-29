import sys
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from downloaders import defaultDownloader as _defaultDownloader
from downloaders.IDownloader import IDownloader

from .DownloadTarget import DownloadTarget


class DownloaderAdapter:
	__slots__ = ("downloader",)

	def __init__(self, downloader: IDownloader):
		self.downloader = downloader

	def __call__(self, downloadTargets: typing.Mapping[str, DownloadTarget], targetDir: Path) -> typing.Mapping[str, DownloadTarget]:
		for k, v in downloadTargets.items():
			v.fsPath = targetDir / v.role
		# ic(downloadTargets)
		self.downloader(downloadTargets.values())
		return downloadTargets


Downloader = DownloaderAdapter

defaultDownloader = DownloaderAdapter(_defaultDownloader)
