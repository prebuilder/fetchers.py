import typing
from abc import ABC, abstractmethod
from pathlib import Path

from ..DownloadTarget import DownloadTarget
from ..utils.idded import IDded
from ..utils.integrity import parseHashesFile, sumFile


class Verifier(IDded):

	delimiter = "="

	@abstractmethod
	def __call__(self, uris: typing.Mapping[Path, str]):
		raise NotImplementedError()
