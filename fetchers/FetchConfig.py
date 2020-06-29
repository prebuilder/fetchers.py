import typing
from pathlib import Path
from shutil import rmtree

from pantarei import ProgressReporter

from .enums import CleanFetch


class FetchConfig:
	"""Encapsulates the shared info used to download the stuff"""

	__slots__ = ("downloadsTmp", "progressReporter", "shallow", "dontFetch", "gpgmeHome", "rpmRoot")

	def doCleanup(self):
		if self.downloadsTmp.exists():
			rmtree(self.downloadsTmp)

	def doPreparations(self):
		self.doCleanup()
		self.downloadsTmp.mkdir(exist_ok=True, parents=True)

	def __init__(self, downloadsTmp: typing.Optional[Path] = None, progressReporter: typing.Optional[ProgressReporter] = None, shallow: bool = True, dontFetch: bool = False, gpgmeHome: typing.Optional[Path] = None, rpmRoot: typing.Optional[Path] = None):
		"""
		`downloadsTmp` is a dir into which files that are not our final goals (`repomd.xml`, archives before unpacking, etc.) will be downloaded
		`gpgme_home` is a dir to be used for crypto operations by gpgme. gpgme is a library wrapping widely used in package managers. Unfortunately, it disallows fully in-memory operations: gpg relies on keys databases on disk (and one has to create one before any meaningful operations), and gpgme relies on CLI gpg.
		`rpmRoot` is a dir to be used as a librpm root. librpm will put shit into it. Wie dont wat it to put shit into the system."""

		thisDir = Path(".").absolute()

		self.shallow = shallow  # True: shallow fetches without tags, False: full fetches + tags
		self.dontFetch = dontFetch  # don't fetch, only populate version

		if downloadsTmp is None:
			downloadsTmp = thisDir / "downloads"

		if gpgmeHome is None:
			gpgmeHome = thisDir / "gpgme_home"

		if rpmRoot is None:
			rpmRoot = thisDir / "rpm_root"

		if progressReporter is None:
			from pantarei import chosenProgressReporter as progressReporter  # pylint:disable=import-outside-toplevel

		self.downloadsTmp = downloadsTmp
		self.gpgmeHome = gpgmeHome
		self.rpmRoot = rpmRoot
		self.progressReporter = progressReporter
