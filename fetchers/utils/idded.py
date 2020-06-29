from abc import ABC
from base64 import b64encode
from hashlib import blake2b


def computeId(*els):
	b = blake2b(digest_size=16)
	for el in els:
		b.update(el.encode("utf-8"))
	return b64encode(b.digest(), altchars=b"_%")


def re2ID(r: "re.Pattern"):
	return r.pattern + "/" + hex(r.flags)[2:]


class IDded(ABC):
	__slots__ = ()

	marker = None
	idComponents = ()

	@property
	def id(self):
		return computeId(self.delimiter.join((self.marker,) + tuple(c for c in self.idComponents))).decode("ascii")
