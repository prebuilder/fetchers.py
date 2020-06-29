import typing
from pathlib import Path

from . import Verifier


class OpenPGPVerifier(Verifier):
	__slots__ = ("files2verify", "pgpBackend")

	marker = "OpenPGP"

	def __init__(self, files2verify: typing.Iterable[typing.Tuple[bytes, bytes]], backend=None) -> None:
		self.files2verify = files2verify
		if backend is None:
			from OpenPGPAbs import ChosenBackend

			backend = ChosenBackend
		self.pgpBackend = backend()

	def __call__(self, downloadsDir: Path, downloadedTargets: typing.Iterable[str]) -> None:
		downloadedTargetsNames = set(downloadedTargets)

		def preprocessFile(f):
			nonlocal downloadedTargetsNames
			if isinstance(f, str):
				f = downloadsDir / f
			if isinstance(f, Path):
				f = f.read_bytes()
			elif isinstance(f, tuple):
				(name, f) = f
			downloadedTargetsNames -= {name}
			return f

		for file2Verify, signature, fingerprint, keyFile in self.files2verify:
			file2Verify = preprocessFile(file2Verify)
			signature = preprocessFile(signature)
			self.pgpBackend.verifyBlob(file2Verify, signature, keyFingerprint=fingerprint, keyFile=keyFile)

		if downloadedTargetsNames:
			raise Exception("Unverified files:", downloadedTargetsNames)
