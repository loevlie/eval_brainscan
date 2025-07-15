import urllib.request
import ssl

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://drive.google.com/uc?export=download&id=1HDtLfLS90a8LSNzJ_Xik3Tu7RnrhyN3n"
urllib.request.urlretrieve(url, "small_onthedesign.pt")
print("Download complete!")
