.PHONY: all base dados site
PYTHON ?= .venv/bin/python

all: base dados site
base:  ; $(PYTHON) src/build_geo_base.py
dados: ; PYTHONPATH=src $(PYTHON) src/build_dados.py
site:  ; $(PYTHON) src/build_site.py
