from ..FetchConfig import FetchConfig
from . import Discovered, Discoverer

sfMirrors = (
	"datapacket",
	"netix",
	"netcologne",
	"freefr",
	
	"liquidtelecom",
	"iweb",
	"pilotfiber",
	"managedway",
	"gigenet",
	"newcontinuum",
	"astuteinternet",
	"cfhcable",
	"ayera",
	"versaweb",
	"svwh",
	"phoenixnap",
	"ufpr",
	"razaoinfo",
	"jaist",
)


class SourceForgeDiscoverer(Discoverer):
	__slots__ = ("projectName", "pathInProject")

	marker = "SFG"

	@property
	def idComponents(self):
		return (self.projectName, self.pathInProject)

	def __init__(self, projectName: str, pathInProject) -> None:
		self.projectName = projectName
		self.pathInProject = pathInProject

	def getMirrorsList(self):
		return sfMirrors

	def __call__(self, fetchConfig: FetchConfig) -> Discovered:
		raise NotImplementedError()
		["https://" + mirror + ".dl.sourceforge.net/project/" + self.projectName + "/" + self.pathInProject for mirror in self.getMirrorsList()]
