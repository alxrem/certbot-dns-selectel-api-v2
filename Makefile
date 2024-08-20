build:
	python3 -m build

check: build
	twine check dist/*

testrelease: check
	twine upload -r testpypi dist/*

release: check
	twine upload dist/*

.PHONY: testrelease release build check
