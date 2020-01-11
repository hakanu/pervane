import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pervane", # Replace with your own username
    version="0.0.27",
    author="hakanu",
    author_email="hi@hakanu.net",
    description="Plain text backed web based note taking app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hakanu/pervane",
    packages=setuptools.find_packages(),
    install_requires=[
        "flask>=1.1.1",
        "Flask-Caching>=1.8.0",
        "Flask-HTTPAuth>=3.3.0",
        "mistune>=0.8.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    #scripts=['bin/pervane'],
    entry_points={"console_scripts": ["pervane = pervane.cli:main"]},
    include_package_data=True,
)
