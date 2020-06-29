import typing
from abc import abstractmethod
from collections import OrderedDict

from AnyVer import AnyVer

from .FetchConfig import FetchConfig

from .utils.idded import IDded
from .utils.json import json
from .utils.ReprMixin import ReprMixin


class Fetched(ReprMixin):
	__slots__ = ("time", "version", "fetcherID")

	def __init__(self, time: float, version: AnyVer, iD: str) -> None:
		self.time = time
		self.version = version
		self.fetcherID = iD

	@property
	def __dict__(self) -> OrderedDict:
		return OrderedDict((k, getattr(self, k)) for k in self.__class__.__slots__)


class IFetcher(IDded):
	__slots__ = ()

	delimiter = "%"

	@abstractmethod
	def __call__(self, dir, fetchConfig: FetchConfig, versionNeeded: bool = True) -> Fetched:
		raise NotImplementedError()


class IURIFetcher(IFetcher):  # pylint:disable=abstract-method
	__slots__ = ("uri",)

	def __init__(self, uri: str, refspec: typing.Optional[str] = None) -> None:
		self.uri = uri

	@property
	def idComponents(self):
		return (self.uri,)


class IRepoFetcher(IURIFetcher):  # pylint:disable=abstract-method
	__slots__ = ("refspec", "repo")

	@property
	def idComponents(self):
		return super().idComponents + (self.refspec,)

	def __init__(self, uri: str, refspec: typing.Optional[str] = None) -> None:
		super().__init__(uri)
		self.refspec = refspec
		self.repo = None


defaultRepoFetcher = None  # set in tools.git
