__all__ = ("Service", "ServiceDomainBasedDetector", "CodeHostingServiceDefaultBranch", "servicesRegistry")
from abc import ABCMeta, abstractmethod
from urllib.parse import ParseResult as URIParseResult
import typing

servicesRegistry = []

def _convertDomainNameToTuple(s: str) -> typing.Tuple[str]:
	return tuple(el.lower() for el in reversed(s.split(".")) if el)


class ServiceMeta(ABCMeta):
	def __new__(cls, className, parents, attrs, *args, **kwargs):
		res = super().__new__(cls, className, parents, attrs, *args, **kwargs)
		if res._representsRealService():
			servicesRegistry.append(res)
		return res


class Service(metaclass=ServiceMeta):
	@classmethod
	@abstractmethod
	def detect(cls, uri) -> URIParseResult:
		raise NotImplementedError()

	@classmethod
	@abstractmethod
	def genArgs(cls, parsedUri):
		raise NotImplementedError()

	@classmethod
	def _representsRealService(cls):
		return False


class ServiceDomainBasedDetector(Service):  # pylint:disable=abstract-method
	domainParts = None

	@classmethod
	def _representsRealService(cls):
		return bool(cls.domainParts)

	@classmethod
	def _detect(cls, parts) -> URIParseResult:
		return tuple(parts) in cls.domainParts

	@classmethod
	def detect(cls, uri: URIParseResult) -> bool:
		return cls._detect(_convertDomainNameToTuple(uri.netloc))


class CodeHostingServiceDefaultBranch:
	def getRepoTagsRecentToOldest(self):
		return self.getRepoTags()

	def getRepoTags(self):
		for t in self.getRepoTagsInfo():
			yield t["name"]

	def getRepoTagsInfo(self):
		raise NotImplementedError
