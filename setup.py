from setuptools import setup

setup(
    name='docs',
    version='0.1.0',
    py_modules=['docs'],
    install_requires=[
        "click==8.1.3", 
        "google-api-python-client==2.51.0", 
        "google-auth-httplib2==0.1.0", 
        "google-auth-oauthlib==0.5.2"
    ],
    packages=["docs"], 
    entry_points={
        'console_scripts': [
            'docs = docs.main:cli',
        ],
    },
) 
