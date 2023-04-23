import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.question import currency_question
from wellets_cli.util import make_headers

CONFIG_API_URL = "api.url"
CONFIG_API_USERNAME = "api.username"
CONFIG_API_PASSWORD = "api.password"
CONFIG_USER_PREFERRED_CURRENCY = "user-settings.preferred-currency"
SETTABLE_CONFIGS = [CONFIG_USER_PREFERRED_CURRENCY]


@click.group()
def config():
    pass


# @config.command(name="keys")
# def show_config_keys():
#     data = ConfigManager.configs()

#     data = [
#         {
#             "config": config.key(),
#             "description": config.description(),
#             "settable": config.is_settable(),
#             "server_side": config.is_server_side(),
#             "sensitive": config.is_sensitive(),
#         }
#         for config in data
#     ]

#     print(tabulate(data, headers="keys"))


# @config.command(name="show")
# @click.option(
#     "--config",
#     default="local",
#     help="One of the config keys, 'local' or 'all'. Default: 'local'",
# )
# @click.option("--nonsensitive", is_flag=True)
# @click.option("--auth-token")
# def show_config(config, nonsensitive, auth_token):
#     auth_token = auth_token or get_auth_token()
#     headers = make_headers(auth_token)

#     if config in ["all"]:
#         keys = ConfigManager.keys()
#     elif config in ["local"]:
#         keys = ConfigManager.keys(server_side=False)
#     elif ConfigManager.has_key(config):
#         keys = [config]
#     else:
#         print(f"Config '{config}' does not exist")
#         return

#     data = ConfigManager.configs(keys)

#     data = [
#         {
#             "key": config.key(),
#             "value": config.value(headers=headers)
#             if nonsensitive or not config.is_sensitive()
#             else "<sensitive>",
#         }
#         for config in data
#     ]

#     print(tabulate(data, headers="keys"))


# @config.command(name="set")
# @click.argument("config")
# @click.option("--auth-token")
# def set_config(config, auth_token):
#     auth_token = auth_token or get_auth_token()
#     headers = make_headers(auth_token)

#     if not ConfigManager.has_key(config):
#         print(f"Config '{config}' does not exist")
#         return

#     if config not in ConfigManager.keys(settable=True):
#         print(f"Config '{config}' is not settable")
#         return

#     if config == "user-settings.preferred-currency":
#         preferred_currency = api.get_preferred_currency(headers=headers)
#         currencies = api.get_currencies(headers=headers)

#         currency_id = currency_question(
#             currencies, default=preferred_currency
#         ).execute()

#         user_settings = api.set_preferred_currency(
#             data={"currency_id": currency_id}, headers=headers
#         )

#         print(user_settings.id)
