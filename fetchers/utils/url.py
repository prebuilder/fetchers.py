from urllib.parse import urljoin, urlparse, urlunparse


def fixHTTPS(uri):
	if isinstance(uri, str):
		parsed = urlparse(uri)
	else:
		parsed = uri

	parsed = list(parsed)
	parsed[0] = "https"
	return urlunparse(parsed)
