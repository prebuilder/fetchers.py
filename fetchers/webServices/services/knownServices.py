__all__ = ("knownServices",)
from pathlib import Path

from ...utils.json import json

knownServicesFile = Path(__file__).parent.absolute() / "knownServices.json"


def loadKnownServices():
	with knownServicesFile.open("rt") as f:
		knownServicesLoaded = json.load(f)

	knownServicesNew = type(knownServicesLoaded)()
	for k, serviceURIs in knownServicesLoaded.items():
		urisNew = []
		for u in serviceURIs:
			urisNew.append(tuple(u.split(".")))
		knownServicesNew[k] = set(urisNew)
	return knownServicesNew


knownServices = loadKnownServices()
