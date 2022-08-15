# wellets_cli

[![codecov](https://codecov.io/gh/lparolari/wellets-cli/branch/main/graph/badge.svg?token=wellets-cli_token_here)](https://codecov.io/gh/lparolari/wellets-cli)
[![CI](https://github.com/lparolari/wellets-cli/actions/workflows/main.yml/badge.svg)](https://github.com/lparolari/wellets-cli/actions/workflows/main.yml)

## Introduction

wellets-cli is the command line interface for Wellets, a crypto-oriented
financial management tool that allows you to keep under control your money.

> Please note that Wellets does not have (for now) any type of integration with
> blockchain wallets, all management is done manually.

## Install

* With **pip**

```bash
pip install wellets-cli
```

## Usage

```bash
$ wellets_cli --help
Usage: wellets_cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  accumulation
  asset
  config
  currency
  login
  portfolio
  transaction
  transfer
  wallet
  whoami
```

### Commands

* `accumulation` - manage accumulations with different strategies (e.g., DCA)
* `asset` - manage assets: balances, allocations, average load price, entries.
* `config` - manage client config
* `currency` - manage currencies
* `login` - login to wellets
* `portfolio` - manage portfolio: group wallets, show allocation and rebalance.
* `transaction` - manage transactions
* `transfer` - manage transfer across wallets
* `wallet` - manage wallets
* `whoami` - show current logged in user

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
