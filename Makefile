.PHONY: all base dados site
all: base dados site
base:  ; python src/build_geo_base.py
dados: ; PYTHONPATH=src python src/build_dados.py
site:  ; python src/build_site.py
