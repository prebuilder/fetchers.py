import typing
from datetime import datetime

from downloaders.DownloadTarget import DownloadTarget as _DownloadTarget, URIsT


class DownloadTarget(_DownloadTarget):
	__slots__ = ("role", "name", "time")

	def __init__(self, role: str, name: str, uris: URIsT, time: datetime, fsPath: None = None) -> None:
		super().__init__(uris, fsPath)
		self.role = role
		self.name = name
		self.time = time
