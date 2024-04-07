# wellets_cli

[![codecov](https://codecov.io/gh/lparolari/wellets-cli/branch/main/graph/badge.svg?token=wellets-cli_token_here)](https://codecov.io/gh/lparolari/wellets-cli)
[![CI](https://github.com/lparolari/wellets-cli/actions/workflows/main.yml/badge.svg)](https://github.com/lparolari/wellets-cli/actions/workflows/main.yml)

## Introduction

wellets-cli is the command line interface for Wellets, a crypto-oriented
financial management tool that allows you to keep under control your money.

> Please note that Wellets does not have (for now) any type of integration with
> blockchain wallets, all management is done manually.

## Install

```bash
pip install wellets-cli
```

## Usage

```bash
$ wellets_cli --help
Usage: wellets_cli [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  asset         Manage financial assets.
  currency      Manage currencies.
  login         Login with your Wellets credentials.
  portfolio     Manage portfolios (aka logical collection of wallets).
  register      Register a new Wellets account.
  transaction   Manage transactions.
  transfer      Manage transfers.
  wallet        Manage money accounts (aka wallet).
  whoami        Print the information of current user.
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
