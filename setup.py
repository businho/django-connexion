from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'connexion',
        'django',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-django',
        'pytest-flake8-v2',
    ],
)
