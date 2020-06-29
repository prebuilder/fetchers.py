import typing
import tarfile
from pathlib import Path

from fsutilz import isNestedIn

from ...styles import styles
from ..compression import CompressionT
from . import ArchiveFormat


class Tar(ArchiveFormat):
	@staticmethod
	def unpack(archPath: Path, extrDir: Path, config: "FetchConfig", compression: typing.Optional[CompressionT] = None) -> None:
		extrDir = extrDir.resolve()
		packedSize = archPath.stat().st_size
		if compression:
			unpackedSize = compression.extractOriginalSize(archPath, packedSize)
		else:
			unpackedSize = packedSize

		with tarfile.open(archPath, "r" + (":" + compression.id if compression else "")) as arch:
			# todo: unit="B", unit_divisor=1024, unit_scale=True
			with config.progressReporter(unpackedSize, str(styles.operationName("unpacking") + " " + styles.entity("archive"))) as pb:
				for f in arch:
					fp = (extrDir / f.name).absolute()
					if isNestedIn(extrDir, fp):
						if fp.is_file() or fp.is_symlink():
							fp.unlink()
						fp.parent.mkdir(parents=True, exist_ok=True)
						arch.extract(f, extrDir, set_attrs=True)
						pb.report(str(fp.relative_to(extrDir)), incr=f.size)
