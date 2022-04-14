import os
from django_connexion import DjangoApi

def helper(file_name):
    dirname = os.path.dirname(__file__)
    filename = os.path.abspath(os.path.join(dirname, f'../testapp/openapi/{file_name}.yaml'))
    return filename


helloworld_api = DjangoApi(helper('helloworld-api'))
upload_api = DjangoApi(helper('file-upload'))
