import typing
from pathlib import Path
from warnings import warn

warn("We have moved from M$ GitHub to https://codeberg.org/prebuilder/fetchers.py , read why on https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo .")

from AnyVer import AnyVer

from .discoverers import Discoverer
from .downloaders import IDownloader, defaultDownloader
from .FetchConfig import FetchConfig
from .Fetcher import Fetched, IURIFetcher
from .GitRepoFetcher import GitRepoFetcher
from .unpackers import Unpacker
from .verifiers import Verifier


class DiscoverDownloadVerifyUnpackFetcher(IURIFetcher):
	__slots__ = ("discoverer", "unpacker", "verifier", "downloader")

	marker = "DDVU"

	@property
	def idComponents(self):
		return (self.discoverer.id, self.verifier.id, self.unpacker.id)

	def __init__(self, discoverer: Discoverer, verifier: Verifier, unpacker: Unpacker, downloader: IDownloader = None) -> None:
		super().__init__(None)
		self.discoverer = discoverer
		if downloader is None:
			downloader = defaultDownloader
		self.downloader = downloader
		self.verifier = verifier
		self.unpacker = unpacker

	def __call__(self, localPath: Path, config: FetchConfig, versionNeeded: bool = True) -> Fetched:
		localPath = Path(localPath).absolute()

		discovereds = tuple(self.discoverer(config))

		commonVersion = None

		for d in discovereds:
			downloadedFiles = self.downloader(d.targets, config.downloadsTmp)

			assert downloadedFiles
			time = max(f.time for f in downloadedFiles.values())

			if self.verifier is not None:
				self.verifier(config.downloadsTmp, downloadedFiles)
			else:
				warn("Package is unverified!")

			self.unpacker(config, downloadedFiles, localPath)

		return Fetched(time, discovereds[0].version, self.id)
