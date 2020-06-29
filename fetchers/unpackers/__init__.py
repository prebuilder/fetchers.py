import typing
from pathlib import Path

from ..DownloadTarget import DownloadTarget
from ..FetchConfig import FetchConfig
from ..styles import styles
from ..utils.idded import IDded


class Unpacker(IDded):
	marker = "unp"
	delimiter = ","

	def __init__(self, dir2ArtifactsMapping: typing.Mapping[str, str]) -> None:
		self.dir2ArtifactsMapping = dir2ArtifactsMapping

	def __call__(self, config: FetchConfig, downloadedFiles, extrDir: Path):
		raise NotImplementedError()
