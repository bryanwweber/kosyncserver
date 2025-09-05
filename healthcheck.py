from urllib.request import urlopen

url = "http://localhost:8000/healthcheck"
response = urlopen(url)
assert response.status == 200, f"Healthcheck failed with status {response.status}"
assert response.msg == "OK", f"Healthcheck failed with message {response.msg}"
