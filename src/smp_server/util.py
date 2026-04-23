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


		prefix = "[✓] " if ok else "[✗] "
		counter = f"[{count[0]}/{count[1]}] " if len(count) == 2 else ""

		searchresult = (
		    f"[⌕] {search[0]:<{25}} | "
		    f"{search[1]:<{15}} | "
		    f"{search[2]:<{15}} | "
		    f"{search[3]}"
		) if len(search) == 4 else ""

		print(f"{prefix}{counter}{searchresult}{content}")
