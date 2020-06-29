import typing
from os import utime
from pathlib import Path

from fsutilz import isNestedIn, nestPath

import rpm

from ...styles import styles
from ..compression import CompressionT
from . import ArchiveFormat


class RPMPackageUnpackerContext:
	"""This class allows you to iterate files and unpack them from a package.
	https://github.com/rpm-software-management/rpm/pull/1311
	"""

	__slots__ = ("path", "ts", "hdr", "files", "rpmFd", "compressedFd", "archive")

	def __init__(self, path, transactionSet=None):
		self.path = path
		self.ts = transactionSet
		self.rpmFd = None
		self.hdr = None
		self.files = None

	@property
	def fileNo(self):
		"""Returns a file number"""
		return self.rpmFd.fileno()

	def __enter__(self):
		self.rpmFd = rpm.fd(str(self.path), "r")  # RPM-specific file descriptor
		self.hdr = self.ts.hdrFromFdno(self.rpmFd)  # should it be explicitly freed anyhow?
		self.files = rpm.files(self.hdr)  # should it be explicitly freed anyhow?
		self.compressedFd = rpm.fd(self.rpmFd, "r", flags=self.hdr[rpm.RPMTAG_PAYLOADCOMPRESSOR])  # RPM-specific compressed file descriptor
		self.archive = self.files.archive(self.compressedFd, False)
		return self

	def iterFiles(self):  # type: typing.Callable[[], typing.Iterable[typing.Tuple["rpm.file", "rpm.archive"]]]
		for f in self.archive:
			# f is rpm.file
			yield f, self.archive

	def __exit__(self, *args, **kwargs):
		self.archive.close()
		self.compressedFd.close()
		self.rpmFd.close()



class Rpm(ArchiveFormat):
	__slots__ = ("gpgKeys",)

	def __init__(self, gpgKeys):
		self.gpgKeys = gpgKeys

	def unpack(self, archPath: Path, extrDir: Path, config: "FetchConfig", compression: typing.Optional[CompressionT] = None) -> None:
		assert compression is None, "You must not specify a decompressor for RPMs, because they encode their format within them and it is librpm deals with the compression"

		extrDir = extrDir.resolve()
		packedSize = archPath.stat().st_size

		rpmRootPathStr = str(config.rpmRoot.absolute())

		ts = rpm.TransactionSet(rpmRootPathStr)
		tsNoVer = rpm.TransactionSet(rpmRootPathStr, rpm.RPMVSF_MASK_NOSIGNATURES)
		kr = ts.getKeyring()

		for key in self.gpgKeys:
			if isinstance(key, Path):
				key = key.read_bytes()
			rpmKey = rpm.pubkey(key)
			kr.addKey(rpmKey)

		try:
			with RPMPackageUnpackerContext(archPath, ts) as o:
				print("Compression:", o.hdr[rpm.RPMTAG_PAYLOADCOMPRESSOR])
				print("Payload:", o.hdr[rpm.RPMTAG_PAYLOADFORMAT])
				print("Built:", o.hdr[rpm.RPMTAG_BUILDTIME])

				unpackedSize = o.hdr[rpm.RPMTAG_LONGARCHIVESIZE]  # uncompressed payload size
				# unpackedSize = o.hdr[rpm.RPMTAG_LONGSIZE] # Sum of all file sizes

				with config.progressReporter(unpackedSize, str(styles.operationName("unpacking") + " " + styles.entity("rpm package"))) as pb:
					for f, af in o.iterFiles():
						print(o.files, o.arch)
						print(repr(f), repr(af))
						print(f.fx, f.name, f.user, f.group, f.state, f.vflags, f.color)
						print("af.tell()", af.tell())

						fp = nestPath(extrDir, f.name)
						print(extrDir, fp, isNestedIn(extrDir, fp))
						if isNestedIn(extrDir, fp):
							if fp.is_file() or fp.is_symlink():
								fp.unlink()
							fp.parent.mkdir(parents=True, exist_ok=True)
							fp.write_bytes(af.read())
							fp.chmod(f.mode)
							# fp.chown()
							utime(str(fp), (f.mtime, f.mtime))
							# chown(str(fp), f.user, f.group, follow_symlinks=False)
							pb.report(str(fp.relative_to(extrDir)), incr=f.size)

		except rpm.error as ex:
			if ex.args[0] == "public key not available":
				if self.ts is tsNoVer:
					raise
				with self.__class__(pkgPath, tsNoVer) as noVer:
					ex.args += tuple(g.extractFingerprintsFromASignature(noVer.hdr[RPMTag.SIGPGP]))
				raise
			elif ex.args[0] == "public key not trusted":
				pass
			elif ex.args[0] == "error reading package header":
				raise
