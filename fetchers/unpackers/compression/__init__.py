import typing
from pathlib import Path


class Compression:
	id = None

	@staticmethod
	def extractOriginalSize(archPath: Path) -> int:
		raise NotImplementedError()


CompressionT = typing.Type[Compression]
