import requests

url = "https://drive.google.com/uc?export=download&id=1HDtLfLS90a8LSNzJ_Xik3Tu7RnrhyN3n"
response = requests.get(url, verify=False, allow_redirects=True)

with open("small_onthedesign.pt", "wb") as f:
    f.write(response.content)
