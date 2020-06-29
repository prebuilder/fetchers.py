import typing
from os import linesep
from pathlib import Path

import sh
from fsutilz import relativePath
from MempipedPath import MempipedPathRead

from ..DownloadTarget import DownloadTarget

# aria2c = fj.aria2c.bake(_fg=True, **{"continue": "true", "check-certificate": "true", "enable-mmap": "true", "optimize-concurrent-downloads": "true", "j": 16, "x": 16, "file-allocation": "falloc"})
aria2c = sh.Command("/usr/bin/aria2c").bake(_fg=True, **{"continue": "true", "check-certificate": "true", "enable-mmap": "true", "optimize-concurrent-downloads": "true", "j": 16, "x": 16, "file-allocation": "falloc"})


def download(targets: typing.Iterable[DownloadTarget]):
	if not targets:
		return
	args = []

	cwdP = Path(".").absolute()  # https://github.com/aria2/aria2/issues/1137

	for t in targets:
		uris = t.uris
		if not isinstance(uris, str):
			uris = "\t".join(uris)
		args += [uris, linesep, " ", "out=", str(relativePath(t.fsPath, cwdP)), linesep]

	with MempipedPathRead("".join(args)) as pipe:
		aria2c(**{"input-file": pipe})
