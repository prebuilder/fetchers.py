fetchers.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
======
~~[![GitLab Build Status](https://gitlab.com/KOLANICH/fetchers.py/badges/master/pipeline.svg)](https://gitlab.com/KOLANICH/fetchers.py/pipelines/master/latest)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/fetchers.py/badges/master/coverage.svg)~~
~~[![GitHub Actions](https://github.com/prebuilder/fetchers.py/workflows/CI/badge.svg)](https://github.com/prebuilder/fetchers.py/actions/)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/prebuilder/fetchers.py.svg)](https://libraries.io/github/prebuilder/fetchers.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

**We have moved to https://codeberg.org/prebuilder/fetchers.py, grab new versions there.**

Under the disguise of "better security" Micro$oft-owned GitHub has [discriminated users of 1FA passwords](https://github.blog/2023-03-09-raising-the-bar-for-software-security-github-2fa-begins-march-13/) while having commercial interest in success and wide adoption of [FIDO 1FA specifications](https://fidoalliance.org/specifications/download/) and [Windows Hello implementation](https://support.microsoft.com/en-us/windows/passkeys-in-windows-301c8944-5ea2-452b-9886-97e4d2ef4422) which [it promotes as a replacement for passwords](https://github.blog/2023-07-12-introducing-passwordless-authentication-on-github-com/). It will result in dire consequencies and is competely inacceptable, [read why](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

If you don't want to participate in harming yourself, it is recommended to follow the lead and migrate somewhere away of GitHub and Micro$oft. Here is [the list of alternatives and rationales to do it](https://github.com/orgs/community/discussions/49869). If they delete the discussion, there are certain well-known places where you can get a copy of it. [Read why you should also leave GitHub](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

---

Just a lib for fetching source code repositories and precompiled binaries from the net and putting them into FS somewhere.

Why do we need it? When building software you have to get their source code. This lib is mainly for that. It's an abstraction layer, allowing you to

* **discover** the latest release;
* **fetch** its source code and its metadata efficiently;
* **verify** its integrity and **extract version number** using the uniform interface;
* **unpack** the archive/installer if needed, populating the dir with sources.

The interface has 2 stages.
1. You create the object representing what is needed to be done.
2. You trigger the action.

This is done this way because the parts are usually done in differrent places: filling-in the info is done by build framework user, execution of the action is done by the framework itself.

The lib outputs some debug info into the stdout. It is by design - it informs the user on what is going on. Remember - the lib is designed to be used in CLI tools building packages. Some of info can be redirected - you need to select a differrent progress reporter. But other messages are not yet redirectable currently.

Supported ways to fetch the source code:

* Git. You usually need shallow clones, to fetch only what you need. But if you use shallow clones, you don't have tags names, which are an extremily popular way to encode software release version. So you either have to stop using shallow clones, which is inacceptible, or get this in another way. We get it via API of source code hostings. The following are implemented:

    * [GitHub](https://github.com)
    * [GitLab](https://gitlab.com)
    * [Bitbucket](https://bitbucket.org)
    * [Launchpad](https://launchpad.net)
    * ~~[SourceForge](https://sourceforge.net)~~

* Just a https link to an archive. Archives are downloaded, then verified, then unpacked. Some CDNs are explicitly supported for more efficien downloading, using `aria2c` multistreaming:

    * ~~[SourceForge](https://sourceforge.net)~~
    * MirrorBrainz

For the tutorial see [`tutorial.ipynb`](./tutorial.ipynb)[![NBViewer](https://nbviewer.org/static/ico/ipynb_icon_16x16.png)](https://nbviewer.org/urls/codeberg.org/prebuilder/fetchers.py/raw/branch/master/tutorial.ipynb).
