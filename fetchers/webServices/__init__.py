import typing
from urllib.parse import ParseResult as URIParseResult
from urllib.parse import urlencode, urlparse

from .DownloadTarget import *
from .Service import *
from .services import *


def _detectService(uri) -> URIParseResult:
	parsedURI = urlparse(uri)
	for s in servicesRegistry:
		detectionResult = s.detect(parsedURI)
		#ic(s, uri, detectionResult)
		if detectionResult:
			args = s.genArgs(parsedURI)
			return (s, args)


def detectService(uri) -> URIParseResult:
	res = _detectService(uri)
	if res:
		serviceClass, ctorArgs = res
		return serviceClass(**ctorArgs)
