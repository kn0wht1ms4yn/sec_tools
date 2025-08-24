'''

    - given a url
    - return all resources referenced on that page

        src=""
        href=""
        action=""
        data=""
        poster=""
        cite=""
        formaction=""
        fetch("")
    
'''
import re
import requests
import argparse

# define flags
flags = (
    ('src="', '"'),
    ('href="', '"'),
    ('action=', '"'),
    ('data="', '"'),
    ('poster="', '"'),
    ('cite="', '"'),
    ('formaction="', '"'),
    ('fetch\\("\\)', '"')
)

def parse_response(text):
    global flags
    results = []
    for flag in flags:
        pattern = f'{flag[0]}(.*?){flag[1]}'
        matches = re.findall(pattern, text)
        for match in matches:
            results.append(match.strip())
    # remove duplicates
    results = set(results)
    return results

def main():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help="url to scan")
    args = parser.parse_args()
    url = args.url
    if not url:
        url = input()

    # send request to website
    r = requests.get(url)

    # assert HTTP 200 response
    assert r.status_code == 200, 'did not receive an hTTP 200 response'

    # parse resources from response
    results = parse_response(r.text)

    # print results
    for result in results:
        print(result)

main()
