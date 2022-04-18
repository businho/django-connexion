import os
from django.test.client import MULTIPART_CONTENT


def test_accept_file_upload_post_method(client):
    file = '/'.join([os.path.dirname(__file__), 'assets', 'test_file.pdf'])

    with open(file, 'rb') as f :
        response = client.post(
            '/file/upload',
            {
                'my_file': f,
                'file_name': os.path.basename(f.name)
            },
            content_type=MULTIPART_CONTENT
        )

    assert response.status_code == 200
