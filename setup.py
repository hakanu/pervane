import setuptools

with open("README.md", "r") as readme_fh:
    long_description = readme_fh.read()

with open("pervane/version.txt", "r") as version_fh:
    version = version_fh.read()

setuptools.setup(
    name="pervane",
    version=version,
    author="hakanu",
    author_email="hi@hakanu.net",
    description="Plain text backed web based markdown note taking, cloud code editor and knowledge base building app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hakanu/pervane",
    packages=setuptools.find_packages(),
    install_requires=[
        "flask>=1.1.1",
        "Flask-Caching>=1.8.0",
        "Flask-HTTPAuth>=3.3.0",
        "Flask-User>=1.0.2.2",
        "email_validator>=1.1.1",
        "atomicfile>=1.0.1",
        "gunicorn>=20.0.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    #scripts=['bin/pervane'],
    entry_points={"console_scripts": ["pervane = pervane.prod:main"]},
    include_package_data=True,
)
