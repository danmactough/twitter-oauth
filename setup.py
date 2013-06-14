import setuptools

description_path = './README.rst'
description_file = open(description_path, 'r')

long_description = description_file.read()



setuptools.setup(name='twitter_oauth',
                version='0.2.0',
                py_modules=['twitter_oauth'],
                author='Kenko',
                license='MIT License',
                keyword='Twitter',
                install_requires=['oauth2'],
                description='A Python module for Twitter API and OAuth',
                keywords=['Twitter', 'Oauth'],
                author_email='kenko.py@gmail.com',
                url='http://code.google.com/p/twitter-oauth',
                long_description=long_description,
                classifiers=[
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                ],
                )
