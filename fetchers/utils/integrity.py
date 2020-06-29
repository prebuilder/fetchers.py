import base64
import csv
import hashlib
import typing
from io import StringIO

from fsutilz import MMap


def sumStringToASCII(s: str, hashFunc=None, asciifier=None) -> str:
	if hashFunc is None:
		hashFunc = hashlib.sha256
	if asciifier is None:

		def asciifier(x):
			return base64.b64encode(x).decode("ascii")

	return asciifier(hashFunc(s.encode("utf-8")).digest())


def sumFile(path, hashers: typing.Iterable) -> typing.Mapping[str, str]:
	"""Creates an object with hashsums of a file"""
	HObjs = [h() for h in hashers]
	if path.stat().st_size:
		with MMap(path) as m:
			for h in HObjs:
				h.update(m)
	return tuple(h.hexdigest() for h in HObjs)


class HashesFilesDialect(csv.Dialect):
	quoting = csv.QUOTE_NONE
	delimiter = " "
	lineterminator = "\n"


def parseHashesFile(hashes: str):
	res = {}
	with StringIO(hashes) as csvIO:
		for line in csv.reader(csvIO, dialect=HashesFilesDialect):
			res[line[2]] = line[0]

	return res
