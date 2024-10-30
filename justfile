# SPDX-FileCopyrightText: Stefan Tatschner
# SPDX-License-Identifier: CC0-1.0

lint: lint-check-fmt lint-ruff lint-mypy lint-reuse

[private]
lint-mypy:
    mypy devman

[private]
lint-ruff:
    ruff check devman

[private]
lint-check-fmt:
    ruff format --check devman

[private]
lint-reuse:
    reuse lint

fmt:
    ruff format devman
    ruff check --fix devman
