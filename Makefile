BUILDDIR=build
BUILD_NUMBER=0
PYPI_SERVER?=pypi.org
PYPI_INDEX?=https://${PYPI_SERVER}/simple/


help:
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '   make clean                       remove the generated files         '
	@echo '   make fullclean                   clean + remove tox, cache          '
	@echo '   make lint                        run lint checks                    '
	@echo '   make test                        run tests                          '
	@echo '   make develop                     update develop environment         '
	@echo '                                                                       '


develop:
	@${MAKE} clean
	pipenv install -d
	pip install -e .[test]


test:
	pytest tests/ src/ \
            --cov=etools_validator \
            --cov-config=tests/.coveragerc \
            --cov-report=html \
            --cov-report=term


lint:
	flake8 src/ tests/; exit 0;
	isort src/ tests/ --check-only -rc; exit 0;


clean:
	@rm -rf ${BUILDDIR} .pytest_cache src/unicef_attachments.egg-info dist *.xml .cache *.egg-info .coverage .pytest MEDIA_ROOT MANIFEST .cache *.egg build STATIC
	@find . -name __pycache__  -prune | xargs rm -rf
	@find . -name "*.py?" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf
	@rm -f coverage.xml flake.out pep8.out pytest.xml


fullclean:
	rm -fr .tox
	rm -f *.sqlite
	make clean
