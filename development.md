upload new version:

`rm -rf dist build *.egg-info && python3 setup.py sdist bdist_wheel && python3 -m twine upload dist/*`
