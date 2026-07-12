.PHONY: check fix-nav

fix-nav:
	python tools/remove_inner_nav.py
	git status -sb

check:
	python tools/check_links.py
