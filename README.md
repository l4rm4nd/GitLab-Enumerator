# GitLab-Enumerator
Python 3 script to fingerprint GitLab CE/EE instances by public CSS files

## 🐍 Usage - Python3

````
usage: gnum.py [-h] url

GitLab version detector via CSS hash enumeration

positional arguments:
  url         GitLab URL (e.g. https://gitlab.example.com/users/sign_in)

options:
  -h, --help  show this help message and exit
````

## 🐳 Usage - Docker

````
docker run --rm ghcr.io/l4rm4nd/gitlab-enumerator:latest -h
````
