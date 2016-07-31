all:
	@echo "Targets: clean dist html install"

clean:
	@find . -name "core" -exec rm -f {} \;
	@find . -name "*~" -exec rm -f {} \;
	@find . -name "#*#" -exec rm -f {} \;
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "*.pyo" -exec rm -f {} \;
	@find . -name "*.orig" -exec rm -f {} \;
	@find . -name "*.rej" -exec rm -f {} \;
	@rm -f var/*

dist: clean html
	@./makedist

html:
	@python makehtml.py > docs/index.html
	@cat docs/index.html

setup:
	@python setup.py || echo Python not installed. Please install it

install: 
	@python -c "import compileall; compileall.compile_dir('.')"
