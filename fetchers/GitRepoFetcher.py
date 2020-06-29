__all__ = ("GitRepoFetcher",)
import typing
import re
import warnings
from pathlib import Path

import git
from AnyVer import AnyVer, _AnyVer
from git.remote import Remote
from pantarei import ProgressReporter, chosenProgressReporter

from . import Fetcher
from .FetchConfig import FetchConfig
from .Fetcher import Fetched, IRepoFetcher
from .styles import styles
from .webServices import detectService

headBranchExtractionRegExp = re.compile("^\\s*HEAD\\s+branch:\\s+(.+)\\s*$", re.M)


def getRemoteDefaultBranch(remote):
	# get_remote_ref_states
	return headBranchExtractionRegExp.search(remote.repo.git.remote("show", remote.name)).group(1)


def getRemoteTags(remote: Remote):
	for l in getattr(remote.repo.git, "ls-remote")(tags=True).splitlines():
		if l[-1] == "\n":
			l = l[:-1]
			if l[-1] == "\r":
				l = l[:-1]
		yield l.split("\t")[-1].split("/")[-1]


def versionNeededsFromTags(tags):
	for tN in tags:
		v = versionFromGitTag(tN)
		if v:
			yield v


def getLocalTags(repo):
	for t in repo.tags:
		yield t.name


versionRx = re.compile("((\\d+\\.)+\\d+)[\\.\\w-]*")


def versionFromGitTag(lastTag: str) -> typing.Optional[AnyVer]:
	versionFromRepo = versionRx.search(lastTag)
	if versionFromRepo:
		versionFromRepo = versionFromRepo.group(0)
		return AnyVer(versionFromRepo)


def getLastCommitTimestampFromRepo(r: git.Repo) -> float:
	return r.active_branch.commit.committed_datetime.timestamp()


class OurUpdateProgress(git.objects.submodule.root.RootUpdateProgress):
	def __init__(self, *args, pb: ProgressReporter = None, **kwargs):
		self.pb = pb
		self.cur_count = 0
		super().__init__(*args, **kwargs)

	def update(self, op_code, cur_count, max_count=None, message=""):
		cur_count = int(cur_count)
		#self.pb.print(op_code, cur_count, max_count, message)
		delta = cur_count - self.cur_count
		self.pb.report(message, delta)
		self.cur_count = cur_count
		#self.pb.print(self._cur_line)


class GitRepoFetcher(IRepoFetcher):
	__slots__ = ("submodules",)

	marker = "git"

	def __init__(self, uri: str, refspec: typing.Optional[str] = None, submodules: typing.Union[bool, typing.Set[str]] = False):
		super().__init__(uri, refspec)
		self.submodules = submodules

	def __call__(self, localPath: Path, fetchConfig: FetchConfig, versionNeeded: bool = True) -> Fetched:
		localPath = Path(localPath).absolute()

		if not (localPath.exists() and localPath.is_dir()):
			localPath.mkdir()
			#assert (localPath.exists() and localPath.is_dir())

		actName = ""
		if not (localPath / ".git").exists():
			actName = "Clon"
			self.repo = git.Repo.init(str(localPath))  # git.Repo.clone disallows to specify a dir, so we workaround with init + pull
			#assert ( (localPath/".git").exists() )
		else:
			actName = "Pull"
			self.repo = git.Repo(str(localPath))

		try:
			self.repo.remotes["origin"].set_url(self.uri)
			remote = self.repo.remotes["origin"]
		except BaseException:
			remote = self.repo.create_remote("origin", self.uri)

		ver = None
		actingName = actName + "ing"
		with chosenProgressReporter(None, str(styles.operationName(actingName) + " a " + styles.entity("git repo"))) as pb:
			if not fetchConfig.dontFetch:
				gargs = [self.repo.remotes["origin"].name]
				if not self.refspec:
					self.refspec = getRemoteDefaultBranch(remote)

				#pb.print("self.uri", self.uri)
				if versionNeeded:
					s = detectService(self.uri)

					if s:
						pb.print(styles.operationName("Detected") + " " + styles.entity("service") + " " + styles.varContent(repr(s)))
						versions = versionNeededsFromTags(s.getRepoTagsRecentToOldest())
						ver = next(versions)
					else:
						pb.print(styles.entity("Service") + " " + styles.error("is not detected") + " " + styles.operationName("using fallback heuristics..."))
						try:
							tags = getRemoteTags(remote)
							versions = versionNeededsFromTags(tags)
							ver = max(versions)
						except BaseException:
							warnings.warn("Cannot get last tag on remote " + repr(remote))

				gargs.append(self.refspec)
				self.repo.git.checkout(self.refspec, B=True)

				gkwargs = {
					"force": True,
					# "verify-signatures":True,
					"progress": OurUpdateProgress(pb=pb),
					"verbose": True,
				}

				if fetchConfig.shallow:
					gkwargs.update({"depth": 1, "update-shallow": True})
				else:
					gkwargs.update({"tags": True})

				pb.print(styles.operationName(actingName) + " " + styles.varContent(self.uri) + " to " + styles.varContent(str(localPath)) + " ...")
				self.repo.remotes["origin"].fetch(*gargs[1:], **gkwargs)
				self.repo.head.reset(self.repo.remotes["origin"].name + "/" + self.refspec, index=True, working_tree=True)

				pb.print("\b" + styles.operationName(actName + "ed"))

				if self.repo.submodules and self.submodules:
					if isinstance(self.submodules, bool):
						if self.submodules:
							sms = self.repo.submodules
					else:
						sms = []
						for sm in self.repo.submodules:
							if sm.name in self.submodules:
								sms.append(sm)

					if sms:
						pb.print("\b" + styles.operationName("Updating") + " " + styles.entity("submodule") + "s...")

						for sm in sms:
							pb.print("\b" + styles.operationName("Initializing") + " " + styles.entity("submodule") + " " + styles.varContent(repr(sm)) + "...")
							sm.update(init=True)
			else:
				if versionNeeded:
					tags = getLocalTags(self.repo)
					versions = versionNeededsFromTags(tags)
					ver = max(versions)

		if versionNeeded:
			print(styles.entity("version") + " from " + styles.entity("tag") + ": " + styles.varContent(ver))

			if ver is None:
				ver = _AnyVer((), format="", suffixFormat="{hash}", hash=self.repo.active_branch.object.hexsha)
				raise Exception

		return Fetched(getLastCommitTimestampFromRepo(self.repo), ver, self.id)


Fetcher.defaultRepoFetcher = GitRepoFetcher
