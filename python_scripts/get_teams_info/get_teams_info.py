import json
import sys

global supported_images
FILE_TO_BE_READ = './.github/variables/teams.json'
global team_info
global test_suites_json


def test_suites(get_supported_apps=False, test_suite="", image="", release=""):
    pip_supported_teams = json.loads(open(FILE_TO_BE_READ, 'r').read())
    global test_suites_json
    test_suites_json = '{"include":['
    if get_supported_apps:
        get_images(pip_supported_teams)
    else:
        if test_suite == "":
            TEST_SUITE_TO_EXECUTE = sys.argv[1]
        else:
            TEST_SUITE_TO_EXECUTE = test_suite

        if image == "":
            IMAGE = sys.argv[2]
        else:
            IMAGE = image
        
        try:
            release = sys.argv[3]
        except: 
            release = ""

        for i in pip_supported_teams:
            team = pip_supported_teams[i]
            if TEST_SUITE_TO_EXECUTE in team['supported-test-suites']:
                test_suite = team['supported-test-suites'][TEST_SUITE_TO_EXECUTE]['applications']
                if check_image(IMAGE, team['supported-test-suites']):
                    for app in test_suite:
                        info = test_suite[app]
                        test_suites_json += '{"team": "' + i + '", "image": "' + app + '", "component": "' + team[
                            'component'] + '", "url": "' + info['url'] + '", "command": "' + info[
                                                'command'] + '", "framework": "' + info[
                                                'framework'] + '", "report-position": "' + info[
                                                'report-position'] + '", "test-type": "' + TEST_SUITE_TO_EXECUTE + '", "release": "' + release + '"'
                        
                        index = info["url"].rindex("/")
                        if 'images' not in info:
                         test_suites_json += ', "app-repo": "' + info["url"][index + 1:] + '"'

                        if 'username-and-password-id' in info:
                            test_suites_json += ', "username": "' + info['username-and-password-id'] + '"'
                        if 'container' in info:
                            test_suites_json += ', "container": "' + info['container'] + '"'
                        if 'java-version' in info:
                            test_suites_json += ', "java-version": "' + info['java-version'] + '"'
                        if 'secrets' in info:
                            test_suites_json += ', "secrets": "' + info['secrets'] + '"'

                        if 'version-id' in info:
                            test_suites_json += ', "version-id": "' + info['version-id'] + '"'

                        if 'images' in info:
                            test_suites_json += ', "images": "' + IMAGE + '"'
                            test_suites_json += ', "version-id": "' + info["images"][IMAGE]["version-id"] + '"'
                            index = info["images"][IMAGE]["url"].rindex("/")
                            test_suites_json += ', "urlCode": "' + info['images'][IMAGE]["url"] + '"'
                            test_suites_json += ', "app-repo": "' + info["images"][IMAGE]["url"][index + 1:] + '"'

                        if 'environment' in info:
                            test_suites_json+= ', "environment": "'+ info['environment'] +'"'

                    test_suites_json += '},'

        test_suites_json = test_suites_json[:-1]
        test_suites_json += ']}'

        if 'url' not in test_suites_json:
            test_suites_json = '{"include":[{ "no-test-found": "True" }]}'
        sys.stdout.write('{}'.format(test_suites_json))


def check_image(image, json_section):
    for test_suite in json_section:
        if json_section[test_suite]['multi-image'] == "true":
            for k in json_section[test_suite]['applications']:
                return isPresentImage(image, json_section[test_suite]['applications'][k]['images'])
        else:
            return isPresentImage(image, json_section[test_suite]['applications'])


def isPresentImage(image, json_section):
    return image in json_section


def returnCommitImage():
    get_images(
        json.loads(open(FILE_TO_BE_READ, 'r').read()), print_mode=False)
    imageCommit = sys.argv[1]
    global supported_images
    listImages = supported_images
    for images in listImages:

        if imageCommit.__contains__(images.replace('awp-', '')):
            print(images)
            break


def get_images(json_section, print_mode=True):
    global supported_images
    supported_images = []

    for i in json_section:
        team = json_section[i]['supported-test-suites']
        for test_suite in team:

            for k in team[test_suite]['applications']:

                if team[test_suite]['multi-image'] == "true":

                    supported_images = supported_images + list(team[test_suite]['applications'][k]['images'].keys())

                else:

                    supported_images = supported_images + list(team[test_suite]['applications'].keys())

    supported_images = list(dict.fromkeys(supported_images))
    if print_mode:
        sys.stdout.write(','.join(supported_images))


def get_images_from_team_name(default=None):
    if default is None:
        team_name = sys.argv[1]
    else:
        team_name = default
    team_name_section = json.loads(open(FILE_TO_BE_READ, 'r').read())[team_name]
    global team_info
    team_info = _retrieve_all_images_from_team(team_name_section)
    print(json.dumps(team_info))


def _retrieve_all_images_from_team(team_name):
    if isinstance(team_name, dict):
        for key, value in team_name.items():
            if key == "images" and isinstance(value, dict):
                return value
            else:
                result = _retrieve_all_images_from_team(value)
                if result is not None:
                    return result

    elif isinstance(team_name, list):
        for item in team_name:
            result = _retrieve_all_images_from_team(item)
            if result is not None:
                return result
    return None