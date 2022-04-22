# Cert Host Scraper

![CI](https://github.com/inverse/cert-host-scraper/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)
![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)
[![License](https://img.shields.io/github/license/inverse/cert-host-scraper.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Query the certificate transparency log for a keyword and check the status code of the results. Optionally filtering out based on the code.

## Usage

```bash
cert-host-scraper search your-domain.com [--status-code 200]
```

## Installation

With pipx:

```bash
pipx install cert-host-scraper
```

With pip:

```bash
pip install cert-host-scraper
```

## Licence

MIT
