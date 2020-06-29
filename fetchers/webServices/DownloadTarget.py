import typing
from abc import ABC, abstractmethod
from datetime import datetime

from AnyVer import AnyVer

from ..utils.ReprMixin import ReprMixin


class ComparableDownloadTarget(ABC):
	__slots__ = ()

	@abstractmethod
	def cmpTuple(self) -> tuple:
		raise NotImplementedError()

	def __lt__(self, other):
		return self.cmpTuple() < other.cmpTuple()

	def __gt__(self, other):
		return self.cmpTuple() > other.cmpTuple()

	def __eq__(self, other):
		return self.cmpTuple() == other.cmpTuple()


class DownloadTargetFile(ComparableDownloadTarget, ReprMixin):
	__slots__ = ("role", "name", "created", "modified", "uri", "size")

	def __init__(self, role: typing.Optional[str], name: str, created: datetime, modified: datetime, uri: str, size: int) -> None:
		self.created = created
		self.modified = modified
		self.uri = uri
		self.role = role
		self.name = name
		self.size = size

	def cmpTuple(self):
		return (self.created, self.modified)

	def __str__(self):
		return self.role + "<" + self.uri + ">"


class DownloadTarget(ComparableDownloadTarget, ReprMixin):
	__slots__ = ("name", "version", "prerelease", "draft", "created", "published", "files")

	def __init__(self, name: str, version: str, prerelease: bool, draft: bool, created: datetime, published: datetime, files: typing.Dict[typing.Optional[str], DownloadTargetFile]) -> None:
		self.name = name
		self.version = AnyVer(version)
		self.prerelease = prerelease
		self.draft = draft
		self.created = created
		self.published = published
		self.files = files

	def cmpTuple(self):
		return (self.created, self.published)

	def __str__(self) -> str:
		return self.name + " [" + self.version + ", " + ("pre" if self.prerelease else "") + "release" + "] <" + repr(self.files) + ">"
