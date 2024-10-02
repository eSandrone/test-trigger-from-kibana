import json
import sys
import requests
import re
from requests.auth import HTTPBasicAuth
# from atlassian import Confluence

# DATA
basic = HTTPBasicAuth(sys.argv[2], sys.argv[3])
FILE_TO_BE_READ = './.github/variables/teams.json'
global test_suites_json

def get_data_from_confluence() -> str:
    # Page with existing AWP version
    url = 'https://atc.bmwgroup.net/confluence/rest/api/content/3307627892/history/0/macro/id/d0d2bb5b-45b6-4f55-ab68-1033a191f957'
    # Make a GET request to the Confluence API
    response = requests.get(url, auth=basic)

    # If the request was successful, release and sprint are recovered
    if response.status_code == 200:
        page_content = response.json()
        next_releases_index = [next_release.start() for next_release in re.finditer(r'"tick" /> / ', page_content['body'])]
        table = page_content['body'][next_releases_index[-2]:next_releases_index[-1]]
        release = table.split('ri:content-title="AWP ')[1].split('"')[0]
        return release
    else:
        print(f"Error: {response.status_code} - Unable to fetch page content") 

def test_suites(test_suite, release) -> None:
    pip_supported_teams = json.loads(open(FILE_TO_BE_READ, 'r').read())
    global test_suites_json
    test_suites_json = '{"include":['
    TEST_SUITE_TO_EXECUTE = test_suite
    RELEASE = release
    for i in pip_supported_teams:
        team = pip_supported_teams[i]
        if TEST_SUITE_TO_EXECUTE in team['supported-test-suites']:
            test_suite = team['supported-test-suites'][TEST_SUITE_TO_EXECUTE]['applications']
            for app in test_suite:
                info = test_suite[app]
                test_suites_json += '{"component": "' + team['component'] + '", "url": "' + info['url'] + '", "command": "' + info['command'] + '", "framework": "' + info['framework'] + '", "report-position": "' + info['report-position'] + '", "test-type": "' + TEST_SUITE_TO_EXECUTE + '", "release": "' + RELEASE + '"'
                optional_keys = ['requirements', 'java-version', 'node-version', 'need-chrome', 'runner']
                for key in info:
                    if key in optional_keys:
                        test_suites_json += f', "{key}": "{info[key]}"'
                test_suites_json += '},'
    test_suites_json = test_suites_json[:-1]
    test_suites_json += ']}'
    if 'url' not in test_suites_json:
        test_suites_json = '{"include":[{ "no-test-found": "True" }]}'
    sys.stdout.write('{}'.format(test_suites_json))

if __name__ == '__main__':
    # release = get_data_from_confluence()
    test_suites(sys.argv[1], "1.0")