test = async () => {
  const response = await fetch("/api/tracks?artist:Basement")
  const data = await response.json()
  data.forEach(element => {
    document.body.innerHTML = data
  })
}
test()
