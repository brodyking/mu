class Color:
	# Standard Colors (Lower Intensity)
	@staticmethod
	def red(s): return("\033[31m{}\033[00m".format(s))
	@staticmethod
	def green(s): return("\033[32m{}\033[00m".format(s))
	@staticmethod
	def yellow(s): return("\033[33m{}\033[00m".format(s))
	@staticmethod
	def blue(s): return("\033[34m{}\033[00m".format(s))
	@staticmethod
	def purple(s): return("\033[35m{}\033[00m".format(s))
	@staticmethod
	def cyan(s): return("\033[36m{}\033[00m".format(s))

	# Bright/Light Colors (90-97 range)
	@staticmethod
	def light_gray(s): return("\033[37m{}\033[00m".format(s))
	@staticmethod
	def black(s): return("\033[90m{}\033[00m".format(s)) # Bright Black / Dark Gray
	@staticmethod
	def light_red(s): return("\033[91m{}\033[00m".format(s))
	@staticmethod
	def light_green(s): return("\033[92m{}\033[00m".format(s))
	@staticmethod
	def light_yellow(s): return("\033[93m{}\033[00m".format(s))
	@staticmethod
	def light_blue(s): return("\033[94m{}\033[00m".format(s))
	@staticmethod
	def pink(s): return("\033[95m{}\033[00m".format(s))
	@staticmethod
	def light_cyan(s): return("\033[96m{}\033[00m".format(s))
	@staticmethod
	def white(s): return("\033[97m{}\033[00m".format(s))

class Util:

	@staticmethod
	def Print(content: str, **kwargs):
		"""
		Prints to the terminal
		- ok (bool): Shows checkmark or X. Defaults to True.
		- count (list): [current, total]. Defaults to empty.
		- search (list): [title,artist,album,location]. Defaults to empty.
		"""


		ok = kwargs.get('ok', True)
		count = kwargs.get('count', [])
		search = kwargs.get('search', [])


		prefix = Color.green("[✓] ") if ok else Color.red("[✗] ")
		counter = f"[{count[0]}/{count[1]}] " if len(count) == 2 else ""

		def fmt(text, width):
		    text = str(text or "")
		    if len(text) > width:
		        return text[:width-2] + ".."
		    return text.ljust(width)

		favorited = "♥ " if search[1] == 1 else "  "

		searchresult = (
		    f"[⌕] {Color.red(fmt(f"{favorited}{search[2]}", 25))} | "
			f"{fmt(search[4], 15)} | "
		    f"{fmt(search[6], 15)} | "
		    f"{Color.blue(search[10])}"
		) if len(search) != 0 else ""
		
		print(f"{prefix}{counter}{searchresult}{content}")
