MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

PY_FILES:=$(shell ls sketchfab/*.py scripts/sketchfab)
PACKAGE_FILES:=$(shell find dist/)

all: package doc

doc:
	pdoc3 --html --force sketchfab

doc-server:
	pdoc3 --http localhost:8080 sketchfab

$(PACKAGE_FILES): $(PY_FILES)
	python3 setup.py sdist bdist_wheel
	touch dist build

package: $(PACKAGE_FILES)

install:
	pip3 install .

clean:
	rm html dist build sketchfab.egg-info

publish: package
	twine upload dist/*
