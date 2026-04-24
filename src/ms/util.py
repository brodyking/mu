import subprocess

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
	def print(content: str, **kwargs):
		"""
			Prints to the terminal
			- ok (bool): Shows checkmark or X. Defaults to True.
			- count (list): [current, total]. Defaults to empty.
			- track (list): The data pulled from the SQLite DB. Defaults to empty.
		"""


		ok = kwargs.get('ok', True) # Status. Shows check or x.
		count = kwargs.get('count', []) # Used to display progress in anticipation of another print.
		track = kwargs.get('track', []) # 

		def fmt(text, width):
		    text = str(text or "")
		    if len(text) > width:
		        return text[:width-2] + ".."
		    return text.ljust(width)

		prefix = Color.green("[] ") if ok else Color.red("[] ")
		counter = f"[{str(count[0]).rjust(len(str(count[1])),"0")}/{count[1]}] " if len(count) == 2 else ""
		favorited = Color.red("󰋑 ") if len(track) != 0 and track[1] == 1 else Color.light_gray("♥ ")

		searchresult = (
			f"[] "
			f"{Color.light_gray('#'+str(track[0]).rjust(4, "0"))} "
		    f"{favorited}{Color.red(fmt(f"{track[2]}", 25))} | "
			f"{fmt(track[4], 15)} | "
		    f"{fmt(track[6], 15)} | "
		    f"{Color.blue(track[10])}"
		) if len(track) != 0 else ""
		
		print(f"{prefix}{counter}{searchresult}{content}")

	@staticmethod
	def promptBool(content:str) -> bool:
		"""
			Asks the user a question, returns the users chioce.
		"""
		print(Color.yellow("[]"),end="")
		while (True):
			response = input(f" {content} (y/n) ")
			if response == "y" or response == 1 or response == "yes":
				return True
			elif response == "n" or response == 0 or response == "no":
				return False


	@staticmethod
	def mpv(track_paths: list) -> None:
		"""
		Plays a list of files in mpv
		"""
		subprocess.run(["mpv"] + track_paths)

