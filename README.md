# python_project_template

A template repository for Python 🐍 projects. This template includes a recommended project structure, automated testing, and documentation generation using [MkDocs](https://www.mkdocs.org/).

---

## Features

- Standard Python project layout
- Automated virtual environment setup
- Build scripts for wheel packaging
- Integrated unit testing with pytest and coverage reporting
- Documentation generation with MkDocs

---

## Getting Started

### 1. Set up the environment

Create and activate a virtual environment, and install dependencies:

```sh
scripts/venv_setup.bat
```

### 2. Build the wheel package

Generate a distributable `.whl` file:

```sh
scripts/build_wheel_package.bat
```

### 3. Run tests

Execute all test cases and generate a coverage report:

```sh
scripts/run_pytests_with_report.bat
```

Test results and coverage reports will be available in the `tests/report/` directory.

---

## Documentation

Documentation is written in Markdown and built using MkDocs. To build and serve the documentation locally:

```sh
mkdocs serve
```

The documentation will be available at [http://localhost:8000](http://localhost:8000).

---

## Project Structure

```
src/
    python_project_template/
        app.py
        __init__.py
tests/
    test_my_package.py
scripts/
    venv_setup.bat
    build_wheel_package.bat
    run_pytests_with_report.bat
    deploy_docs_to_github.bat
docs/
    index.md
    reference_manual.md
```
