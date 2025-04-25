# Переменные
POETRY = poetry
PYENV = pyenv

VENV_PATH = .venv
PYTHON_VERSION = 3.12
SRC_DIR = src

.PHONY: help
help:
	@echo "Пожалуйста используйте 'make <target>' где <target> одно значение из:"
	@echo ""
	@echo "  install     Установка зависимостей и настройка окружения"
	@echo "  update      Обновление зависимостей"
	@echo "  clean       Очистка окружения"
	@echo "  format      Форматирование кода:"
	@echo "  test        Запуск тестов"
	@echo "  shell       Запуск интерактивного шелла"
	@echo ""
	@echo "Ознакомьтесь с содержимом Make файла для уточнения состава комманд."
# Основные цели
all: ruff test

setup: pyenv poetry_venv

# Цель "pyenv"
pyenv:
	$(PYENV) install -s $(PYTHON_VERSION)
	$(PYENV) local $(PYTHON_VERSION)

# Цель "poetry_venv"
poetry_venv:
	$(POETRY) env use $(PYTHON_VERSION)
	$(POETRY) config virtualenvs.in-project true

# Цель "lock"
lock:
	$(POETRY) lock --no-update

make_dirs:
	mkdir -p .docker/postgres

# Цель "install"
install_nl: setup
	$(POETRY) install  --no-root


pre_install: setup lock make_dirs
	$(POETRY) install  --no-root

install: pre_install
	$(POETRY) run pre-commit install

# Цель "update"
update:
	$(POETRY) update

# Цель "shell"
shell: poetry_venv
	$(POETRY) shell

# Цель "format"
format:
	$(POETRY) run ruff format $(SRC_DIR) && $(POETRY) run ruff check --fix   $(SRC_DIR)

# Цель "test"
test:
	$(POETRY) run pytest -v --cov=. --cov-report xml:cov.xml || true

# Цель "clean"
clean:
	rm -rf $(VENV_PATH)
	find . -path "./.docker" -prune -o -type d -name "__pycache__"  -exec rm -r {} +
	find . -path "./.docker" -prune -o -type f -name "*.pyc"  -exec rm -f {} +
	git config --unset-all core.hooksPath

# Цель "check" для линтинга и тестов одновременно
check: format test


.PHONY: all shell format setup pyenv poetry_venv install update flake test clean check
