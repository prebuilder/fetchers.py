try:
	from RichConsole import groups

	class styles:
		# pylint:disable=no-member
		success = groups.Fore.lightgreenEx
		operationName = groups.Fore.yellow
		entity = groups.Fore.lightblueEx
		varContent = groups.Fore.lightmagentaEx
		error = groups.Fore.lightredEx


except ImportError:

	class styles:
		success = operationName = entity = varContent = error = lambda x: x
