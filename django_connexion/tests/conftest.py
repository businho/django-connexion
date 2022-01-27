import pathlib

import pytest

TEST_FOLDER = pathlib.Path(__file__).parent
FIXTURES_FOLDER = TEST_FOLDER / 'fixtures'


@pytest.fixture(scope='session')
def django_api_spec_dir():
    return FIXTURES_FOLDER / 'django'
