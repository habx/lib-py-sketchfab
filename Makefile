MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

PY_FILES:=$(shell ls sketchfab/*.py scripts/sketchfab)
PACKAGE_FILES:=build dist
#$(shell find dist/)

all: package doc

doc: html

html: $(PY_FILES) README.md
	pdoc3 --html --force sketchfab
	touch html

doc-server:
	pdoc3 --http localhost:8080 sketchfab

$(PACKAGE_FILES): $(PY_FILES)
	rm -Rf dist build
	python3 setup.py sdist bdist_wheel

package: $(PACKAGE_FILES)

install:
	pip3 install .

clean:
	rm html dist build sketchfab.egg-info

publish: package
	twine upload dist/*

docker:
	docker rmi -f sketchfab ; docker build . -t sketchfab

run:
	alias sketchfab="$(shell pwd)/scripts/sketchfab" && PYTHONPATH=$(shell pwd) ${SHELL}
