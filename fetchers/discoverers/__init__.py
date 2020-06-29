import typing
from abc import abstractmethod

from AnyVer import AnyVer

from ..utils.idded import IDded

from ..DownloadTarget import DownloadTarget
from ..FetchConfig import FetchConfig

from ..webServices import DownloadTarget as ServiceDownloadTarget, DownloadTargetFile


class Discovered:
	__slots__ = ("version", "targets")

	def __init__(self, version: AnyVer, targets: typing.Mapping[str, DownloadTarget]) -> None:
		self.version = version
		self.targets = targets


class Discoverer(IDded):
	__slots__ = ()

	delimiter = "@"

	@abstractmethod
	def __call__(self, fetchConfig: FetchConfig) -> Discovered:
		raise NotImplementedError()
