import pytest
import pycurl
import io
import json


def test_upload():
    c = pycurl.Curl()
    b = io.BytesIO()
    c.setopt(pycurl.URL, 'http://localhost:8088/upload')
    c.setopt(pycurl.HTTPHEADER,
             ['Accept:application/json', 'Content-Type: multipart/form-data'])
    c.setopt(pycurl.HTTPPOST,
             [('file',
               (pycurl.FORM_FILE,
                'static/img/images/7-action-athlete-896567.jpg'))])
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    assert c.getinfo(pycurl.RESPONSE_CODE) == 200
    c.close()

    response = b.getvalue()
    response = json.loads(response)[0]

    assert (response['file_name']
            == 'static/img/images/MAX-7-action-athlete-896567.jpg')
    assert response['caption'] == 'a baseball player swinging a bat at a ball'


if __name__ == '__main__':
    pytest.main([__file__])
