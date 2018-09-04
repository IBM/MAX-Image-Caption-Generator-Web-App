import pytest
import re
import requests


# URL endpoints
test_url = 'http://localhost:8088'
upload_url = test_url + '/upload'
detail_url = test_url + '/detail'
cleanup_url = test_url + '/cleanup'

# Test message strings
no_server_msg = 'Start web app server at ' + test_url + ' to run tests'

detail_400_msg = '400: Missing image parameter'
detail_404_msg = '404: Image not found'

# Test File Paths
test_file = 'static/img/images/7-action-athlete-896567.jpg'
temp_file_regex = r'^static/img/images/MAX-(.*?)-7-action-athlete-896567\.jpg$'
caption_part = 'baseball'

test_file_2 = 'static/img/images/ball-court-design-209977.jpg'
temp_file_2_regex = r'^static/img/images/MAX-(.*?)-ball-court-design-209977\.jpg$'
caption_part_2 = 'tennis'

invalid_file = 'static/favicon.ico'

# Session and cookies
key_base = 'max-image-caption-generator-web-app'
session = requests.Session()
session2 = requests.Session()


@pytest.mark.skipif("Helper function")
def check_server_up():
    global server_up

    if 'server_up' not in globals():
        try:
            r = session.get(test_url)
            server_up = r.status_code == 200
            if server_up:
                session2.get(test_url)
        except requests.exceptions.ConnectionError:
            server_up = False

    return server_up


def test_server():
    assert check_server_up() is True, no_server_msg


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_upload_success():
    with open(test_file, 'rb') as file:
        file_form = {'file': file}
        r = session.post(url=upload_url, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert re.match(temp_file_regex, response[0]['file_name'])
    assert caption_part in response[0]['caption']


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_upload_failure():
    with open(invalid_file, 'rb') as file:
        file_form = {'file': file}
        response = session.post(url=upload_url, files=file_form)

    assert response.status_code == 400


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_multiple_file_upload():
    with open(test_file, 'rb') as file, open(test_file_2, 'rb') as file2:
        file_form = [('file', file), ('file', file2)]
        r = session.post(url=upload_url, files=file_form)

    assert r.status_code == 200
    response = r.json()

    global temp_file
    temp_file = response[0]['file_name']

    assert re.match(temp_file_regex, temp_file)
    assert caption_part in response[0]['caption']
    assert re.match(temp_file_2_regex, response[1]['file_name'])
    assert caption_part_2 in response[1]['caption']


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_detail_success():
    img_detail_url = detail_url + '?image=' + temp_file
    r = session.get(img_detail_url)
    assert r.status_code == 200


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_delete():
    r = session.delete(cleanup_url)
    assert r.status_code == 200


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_detail_failure():
    r = session.get(detail_url)
    assert r.status_code == 400
    assert detail_400_msg in r.text

    img_detail_url = detail_url + '?image=' + temp_file
    r = session.get(img_detail_url)
    assert r.status_code == 404
    assert detail_404_msg in r.text


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_muliple_users():
    with open(test_file, 'rb') as file:
        file_form = {'file': file}
        r = session.post(url=upload_url, files=file_form)

    with open(test_file, 'rb') as file:
        file_form = {'file': file}
        r2 = session2.post(url=upload_url, files=file_form)

    assert r.status_code == 200
    assert r2.status_code == 200
    response = r.json()
    response2 = r2.json()
    assert re.match(temp_file_regex, response[0]['file_name'])
    assert re.match(temp_file_regex, response2[0]['file_name'])
    assert response[0]['file_name'] != response2[0]['file_name']

    img_detail_url = detail_url + '?image=' + response2[0]['file_name']
    dtr = session.get(img_detail_url)
    assert dtr.status_code == 404

    dlr = session2.delete(cleanup_url)
    assert dlr.status_code == 200

    img_detail_url = detail_url + '?image=' + response[0]['file_name']
    dtr2 = session.get(img_detail_url)
    assert dtr2.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
