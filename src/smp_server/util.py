class Util:

	@staticmethod
	def Print(content: str,ok: bool=True,count: list=[]):
		"""
			Prints to the terminal. If counting, count takes in [current,total] in a list.	
		"""
		output = ""
		if ok:
			output +="[✓] "
		else:
			output +="[✗] "
		if len(count) == 2:
			output += f"[{count[0]}/{count[1]}] "

		print(f"{output}{content}")

