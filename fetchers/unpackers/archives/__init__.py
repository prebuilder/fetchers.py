import typing
from pathlib import Path

from ...DownloadTarget import DownloadTarget
from ...FetchConfig import FetchConfig
from .. import Unpacker
from ..compression import CompressionT


class ArchiveFormat:
	@staticmethod
	def unpack(archPath: Path, extrDir: Path, progressReporter: "pantarei.ProgressReporter", compression: typing.Optional[CompressionT] = None):
		raise NotImplementedError()


class Archive(Unpacker):
	__slots__ = ("format", "compression")

	marker = "arch"

	@property
	def idComponents(self):
		return (self.format.__name__ if self.format else "", self.compression.id if self.compression else "")

	def __init__(self, dir2ArtifactsMapping: typing.Mapping[str, str], format: ArchiveFormat = None, compression: typing.Optional[CompressionT] = None) -> None:
		super().__init__(dir2ArtifactsMapping)
		self.format = format
		self.compression = compression

	def __call__(self, config: FetchConfig, downloadedTargets: typing.Mapping[str, DownloadTarget], extrDir: Path) -> None:
		assert downloadedTargets

		def enumerateArts():
			if self.dir2ArtifactsMapping is None:
				for art in downloadedTargets.items():
					yield art, extrDir / art.role
			elif isinstance(self.dir2ArtifactsMapping, str):
				yield downloadedTargets[self.dir2ArtifactsMapping], extrDir
			else:
				for destDir, arts in self.dir2ArtifactsMapping.items():
					for artRole in arts:
						yield downloadedTargets[artRole], extrDir / destDir

		for art, extrPath in enumerateArts():
			extrPath.mkdir(exist_ok=True, parents=True)
			self.format.unpack(art.fsPath, extrPath, config, self.compression)
