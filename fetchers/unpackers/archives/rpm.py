import typing
from os import utime
from pathlib import Path

from fsutilz import isNestedIn, nestPath

import rpm
from rpm.highLevel import RPMPackageUnpackerContext

from ...styles import styles
from ..compression import CompressionT
from . import ArchiveFormat


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
