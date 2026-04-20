.PHONY: help install install-dev test test-cov lint format type-check clean pre-commit

help:
	@echo "Targets disponíveis:"
	@echo "  install       Instala dependências de runtime (requirements.txt)"
	@echo "  install-dev   Instala dependências de desenvolvimento e runtime"
	@echo "  test          Executa a suíte de testes com pytest"
	@echo "  test-cov      Executa testes com cobertura"
	@echo "  lint          Executa ruff (lint)"
	@echo "  format        Formata código com black e isort"
	@echo "  type-check    Executa mypy"
	@echo "  pre-commit    Roda pre-commit em todos os arquivos"
	@echo "  clean         Remove artefatos gerados"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest

test-cov:
	pytest --cov=. --cov-report=term-missing --cov-report=xml

lint:
	ruff check .

format:
	isort .
	black .

type-check:
	mypy .

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov build dist *.egg-info coverage.xml .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
