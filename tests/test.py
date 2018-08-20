import pytest
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
temp_file = 'static/img/images/MAX-7-action-athlete-896567.jpg'
test_file_caption = 'a baseball player swinging a bat at a ball'

test_file_2 = 'static/img/images/action-activity-athlete-163487.jpg'
temp_file_2 = 'static/img/images/MAX-action-activity-athlete-163487.jpg'
test_file_2_caption = 'a baseball player pitching a ball on top of a field .'

invalid_file = 'static/favicon.ico'


@pytest.mark.skipif("Helper function")
def check_server_up():
    global server_up

    if 'server_up' not in globals():
        try:
            r = requests.get(test_url)
            server_up = r.status_code == 200
        except requests.exceptions.ConnectionError:
            server_up = False

    return server_up


def test_server():
    assert check_server_up() is True, no_server_msg


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_upload_success():
    with open(test_file, 'rb') as file:
        file_form = {'file': file}
        r = requests.post(url=upload_url, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert response[0]['file_name'] == temp_file
    assert response[0]['caption'] == test_file_caption


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_upload_failure():
    with open(invalid_file, 'rb') as file:
        file_form = {'file': file}
        response = requests.post(url=upload_url, files=file_form)

    assert response.status_code == 400


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_multiple_file_upload():
    with open(test_file, 'rb') as file, open(test_file_2, 'rb') as file2:
        file_form = [('file', file), ('file', file2)]
        r = requests.post(url=upload_url, files=file_form)

    assert r.status_code == 200
    response = r.json()
    assert response[0]['file_name'] == temp_file
    assert response[0]['caption'] == test_file_caption
    assert response[1]['file_name'] == temp_file_2
    assert response[1]['caption'] == test_file_2_caption


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_detail_success():
    img_detail_url = detail_url + '?image=' + temp_file
    r = requests.get(img_detail_url)
    assert r.status_code == 200


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_delete():
    r = requests.delete(cleanup_url)
    assert r.status_code == 200


@pytest.mark.skipif(not check_server_up(), reason=no_server_msg)
def test_detail_failure():
    r = requests.get(detail_url)
    assert r.status_code == 400
    assert detail_400_msg in r.text

    img_detail_url = detail_url + '?image=' + temp_file
    r = requests.get(img_detail_url)
    assert r.status_code == 404
    assert detail_404_msg in r.text


if __name__ == '__main__':
    pytest.main([__file__])
