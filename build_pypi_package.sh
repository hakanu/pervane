echo "Building the package"
python3 setup.py sdist bdist_wheel 

echo "now uploading to pypi repo"
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*