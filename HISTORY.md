Changelog
=========


(unreleased)
------------

Fix
~~~
- Set production config as default. [lparolari]

Other
~~~~~
- Chore: migrate .json() pydantic. [lparolari]
- Feat: visualize ema on price chart. [lparolari]
- Ci: upgrade python version to 3.12. [lparolari]


1.9.1 (2024-03-17)
------------------
- Release: v1.9.1. [lparolari]
- Chore: fix linting warnings. [lparolari]
- Chore: fmt. [lparolari]
- Chore: migrate pydantic v2. [lparolari]
- Chore: bump packages versions. [lparolari]


1.9.0 (2023-12-03)
------------------
- Release: v1.9.0. [lparolari]
- Feature: add show capital gain. [lparolari]


1.8.1 (2023-12-03)
------------------
- Release: v1.8.1. [lparolari]
- Feat: toggle desc for wallet. [lparolari]


1.8.0 (2023-11-04)
------------------
- Release: v1.8.0. [lparolari]
- Feat: add wallet show + description field. [lparolari]
- Feat: add api error handler. [lparolari]


1.7.1 (2023-10-03)
------------------
- Release: v1.7.1. [lparolari]
- Chore: update dependencies. [lparolari]


1.7.0 (2023-10-01)
------------------

Fix
~~~
- Use settings' date_format in wallets list. [lparolari]

Other
~~~~~
- Release: v1.7.0. [lparolari]
- Chore: rename get wallet balance command. [lparolari]
- Feat: add set wallet balance command. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat: remove accumulation id from transaction create. [lparolari]
- Merge branch 'feature/command-docs' (#4) [lparolari]

  * feature/command-docs:
    feat: add docs for transfer
    feat: add docs for transaction
    feat: add docs for portfolio
    feat: marked as deprecated investment command
    feat: add docs for currency
    feat: add docs for asset
    feat: add docs for login and register
    feat: add docs for wallet
    feat: add docs for whoami
- Feat: add docs for transfer. [lparolari]
- Feat: add docs for transaction. [lparolari]
- Feat: add docs for portfolio. [lparolari]
- Feat: marked as deprecated investment command. [lparolari]
- Feat: add docs for currency. [lparolari]
- Feat: add docs for asset. [lparolari]
- Feat: add docs for login and register. [lparolari]
- Feat: add docs for wallet. [lparolari]
- Feat: add docs for whoami. [lparolari]


1.6.0 (2023-04-30)
------------------
- Release: v1.6.0. [lparolari]
- Feat: add asset visualize command. [lparolari]
- Feat: plot asset allocation. [lparolari]


1.5.1 (2023-04-24)
------------------
- Release: v1.5.1. [lparolari]
- Chore: update codecov dep. [lparolari]

  should fix ci error on `make install` saying "Unable to find installation candidates for codecov (2.1.12)"
- Chore: remove rename workflow. [lparolari]


1.5.0 (2023-04-23)
------------------

Fix
~~~
- Allow credential not in .secrets.toml. [lparolari]

Other
~~~~~
- Release: v1.5.0. [lparolari]
- Chore: fix linting. [lparolari]
- Chore: formatter. [lparolari]
- Chore: accumulation command deprecated. [lparolari]
- Chore: remove config command. [lparolari]
- Feat: show chart based on settings. [lparolari]
- Chore: update configs with env. [lparolari]
- Chore: replace custom config impl with dynaconf (#1) [lparolari]


1.4.0 (2023-04-23)
------------------

Fix
~~~
- Unused import. [lparolari]

Other
~~~~~
- Release: v1.4.0. [lparolari]
- Feat: show asset history. [lparolari]
- Feat: prettify asset allocation. [lparolari]
- Feat: prettify asset entries. [lparolari]
- Feat: improve readability of portfolio list. [lparolari]
- Feat: enhance percent number print. [lparolari]


1.3.0 (2023-03-19)
------------------
- Release: v1.3.0. [lparolari]
- Feat: sync currency rates. [lparolari]
- Chore: update config manager. [lparolari]


1.2.0 (2022-12-04)
------------------

Fix
~~~
- Require confirmation before transaction revert. [lparolari]

Other
~~~~~
- Release: v1.2.0. [lparolari]
- Feat: show wallet balances. [lparolari]
- Feat: create/list investments. [lparolari]


1.1.2 (2022-11-19)
------------------

Fix
~~~
- Version not found. [lparolari]

Other
~~~~~
- Release: v1.1.2. [lparolari]


1.1.1 (2022-11-19)
------------------
- Release: v1.1.1. [lparolari]
- Chore: add --version. [lparolari]


1.1.0 (2022-11-19)
------------------

Fix
~~~
- Remove balance in wallet creation. [lparolari]
- Prevent division by zero. [lparolari]
- Make release. [lparolari]

Other
~~~~~
- Release: v1.1.0. [lparolari]
- Feat: update wallet. [lparolari]
- Chore: allow to disable rounding. [lparolari]
- Feat: revert list of transactions. [lparolari]
- Chore: update currency formatter. [lparolari]
- Feat: transfer max balance, confirm. [lparolari]


1.0.3 (2022-08-17)
------------------

Fix
~~~
- Remove initial balance for create wallet. [lparolari]

Other
~~~~~
- Release: v1.0.3. [lparolari]
- Chore: add confirmation step for `make release` command. [lparolari]


1.0.2 (2022-08-17)
------------------

Fix
~~~
- Linting errors. [lparolari]
- Linting errors. [lparolari]

Other
~~~~~
- Release: v1.0.2. [lparolari]
- Chore: update CONTRIBUTING.md. [lparolari]
- Release: v1.0.1. [lparolari]
- Release: v1.0.1. [lparolari]
- Chore: update defaults. [lparolari]
- Feat(register): add register. [lparolari]
- Docs: readme and pip project desc. [lparolari]
- Chore: update release command. [lparolari]
- Release: v1.0.0. [lparolari]
- Ci: update release pipeline. [lparolari]
- Feat(config): prettied show/set commands. [lparolari]
- Chore: cleanup. [lparolari]
- Feat(asset): show entries. [lparolari]
- Feat(config): beautify print, set preferred currency. [lparolari]
- Chore: update .gitignore. [lparolari]
- Chore: fmt. [lparolari]
- Chore(transfer): remove disclaimer. [lparolari]
- Fat(transaction): drop dollar rate. [lparolari]
- Feat(wallet): remove average load price. [lparolari]
- Fix(accumulation): belongs to asset instead of wallet. [lparolari]
- Feat(transaction): revert. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(asset): total balance. [lparolari]
- Fix(asset): allocation balance. [lparolari]
- Ci: remove mac tests. [lparolari]
- Ci: fix pipeline. [lparolari]
- Ci: fix poetry. [lparolari]
- Ci: update gh actions. [lparolari]
- Chore: fmt. [lparolari]
- Chore: cleanup, linter errors. [lparolari]
- Chore: switch to poetry. [lparolari]
- Feat(asset): allocation. [lparolari]
- Feat(asset): balance. [lparolari]
- Feat(asset): add average load price. [lparolari]
- Feat(asset): list. [lparolari]
- Chore: cleanup. [lparolari]
- Feat(login): load credentials from env. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(transfer): create transfer. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(accumulation): create entry. [lparolari]


1.0.1 (2022-08-17)
------------------

Fix
~~~
- Linting errors. [lparolari]

Other
~~~~~
- Release: v1.0.1. [lparolari]
- Release: v1.0.1. [lparolari]
- Chore: update defaults. [lparolari]
- Feat(register): add register. [lparolari]
- Docs: readme and pip project desc. [lparolari]
- Chore: update release command. [lparolari]


1.0.0 (2022-08-15)
------------------

Fix
~~~
- Linting errors. [lparolari]
- Empty accumulation list. [lparolari]
- Portfolio weight input validation. [lparolari]
- Get password from stdin. [lparolari]
- Percent formatter. [lparolari]
- Average load price param. [lparolari]
- Typo. [lparolari]
- Remove. [lparolari]

Other
~~~~~
- Release: v1.0.0. [lparolari]
- Ci: update release pipeline. [lparolari]
- Feat(config): prettied show/set commands. [lparolari]
- Chore: cleanup. [lparolari]
- Feat(asset): show entries. [lparolari]
- Feat(config): beautify print, set preferred currency. [lparolari]
- Chore: update .gitignore. [lparolari]
- Chore: fmt. [lparolari]
- Chore(transfer): remove disclaimer. [lparolari]
- Fat(transaction): drop dollar rate. [lparolari]
- Feat(wallet): remove average load price. [lparolari]
- Fix(accumulation): belongs to asset instead of wallet. [lparolari]
- Feat(transaction): revert. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(asset): total balance. [lparolari]
- Fix(asset): allocation balance. [lparolari]
- Ci: remove mac tests. [lparolari]
- Ci: fix pipeline. [lparolari]
- Ci: fix poetry. [lparolari]
- Ci: update gh actions. [lparolari]
- Chore: fmt. [lparolari]
- Chore: cleanup, linter errors. [lparolari]
- Chore: switch to poetry. [lparolari]
- Feat(asset): allocation. [lparolari]
- Feat(asset): balance. [lparolari]
- Feat(asset): add average load price. [lparolari]
- Feat(asset): list. [lparolari]
- Chore: cleanup. [lparolari]
- Feat(login): load credentials from env. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(transfer): create transfer. [lparolari]
- Chore: cosmetic. [lparolari]
- Feat(accumulation): create entry. [lparolari]
- Feat(transaction): allow to set accumulation. [lparolari]
- Feat(accumulation): delete accumulation. [lparolari]
- Feat(accumulation): create accumulation. [lparolari]
- Fix(accumulation): align list api to backend. [lparolari]
- Feat(accumulation): create accumulation dummy. [lparolari]
- Feat(accumulation): list, show and next-entry commands. [lparolari]
- Chore: remove unused field. [lparolari]
- Chore(portfolio): improve ux. [lparolari]
- Chore(wallet): improve listing. [lparolari]
- Faet(wallet): add initial balance on create. [lparolari]
- Feat(transaction): confirm buy. [lparolari]
- Feat(transaction): show buy amount and countervalue in list.
  [lparolari]
- Fix(transaction): compute dollar rate. [lparolari]
- Feat(transaction): ask for created_at, other improvements. [lparolari]
- Chore: align login with inquirerPy. [lparolari]
- Feat(transaction): ask for change currency and value. [lparolari]
- Chore: fmt. [lparolari]
- Chore: print more currency information. [lparolari]
- Feat(currency): list currencies. [lparolari]
- Feat(wallet): show allocation. [lparolari]
- Fix(portfolio): show weight in percent. [lparolari]
- Feat(portfolio): delete. [lparolari]
- Feat(transaction): create new transaction. [lparolari]
- Wip: create transaction. [lparolari]
- Feat(transaction): update transaction list with details. [lparolari]
- Feat(transaction): list transactions by wallet. [lparolari]
- Feat(config): show current config. [lparolari]
- Chore: read  from .env. [lparolari]
- Fix(portfolio): update create with InquirerPy api. [lparolari]
- Feat(portfolio): edit portfolio. [lparolari]
- Feat(portfolio): create new portfolio. [lparolari]
- Feat(portfolio): rebalance show actual weight. [lparolari]
- Feat(portfolio): rebalance. [lparolari]
- Feat(portfolio): show balance. [lparolari]
- Feat(portfolio): list all portfolios. [lparolari]
- Refactor: rename currency model. [lparolari]
- Refactor: rename balance model. [lparolari]
- Feat(wallet): show total balance. [lparolari]
- Feat(wallet): show wallet balance. [lparolari]
- Feat(portfolio): list portfolios. [lparolari]
- Feat(portfolio): add command group. [lparolari]
- Refactor: add base url to api. [lparolari]
- Refactor: move commands to module. [lparolari]
- Refactor: cli and auth. [lparolari]
- Feat(wallet): show wallet average load price. [lparolari]
- Feat(wallet): add countervalue on balance. [lparolari]
- Feat(wallet): delete wallet. [lparolari]
- Chore: improve error clarity. [lparolari]
- Feat: add whoami command. [lparolari]
- Feat: persist auth. [lparolari]
- Chore: remove venv files. [lparolari]
- Feat(wallet): create new wallet. [lparolari]
- Feat(wallet): list wallets. [lparolari]
- ✅ Ready to clone and code. [lparolari]
- Initial commit. [Luca Parolari]


