# PyNeedle Monorepo

![ico](./attachments/needle_ico.png)

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)

This repository contains the source code for the PyNeedle ecosystem, a modern toolkit for decoupling meaning from implementation in Python applications.

---

## About this Repository

This is a monorepo managed with `uv` workspaces. It contains all the packages that make up the PyNeedle runtime.

**➡️ For user-facing documentation, quick start, and API examples, please see the `pyneedle` package [README](./packages/pyneedle/README.md).**

## Core Packages

-   `pyneedle-spec`: Defines the core `Protocol` interfaces for all components.
-   `pyneedle-pointer`: The standard implementation of `SemanticPointer` (`L`) and `PointerSet`.
-   `pyneedle-runtime`: Provides core operators like `FileSystemOperator` and composes other components.
-   `pyneedle`: The user-facing distribution that combines all of the above into a single, easy-to-use namespace package.

## Development Setup

To contribute to PyNeedle, you need to set up a local development environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/quipu-dev/Needle.git
    cd Needle
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install all workspace packages and development dependencies:**
    ```bash
    pip install -e .[dev]
    ```
    This command installs all packages in editable mode and makes them available in your environment.

## Running Tests

To run the test suite, use `pytest`:
```bash
pytest
```

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](./LICENSE) file for details.
