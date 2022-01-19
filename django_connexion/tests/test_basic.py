def test_settings(settings):
    assert settings.INSTALLED_APPS == ['django_connexion.tests.testapp']
