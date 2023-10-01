import click
from InquirerPy import inquirer

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.question import confirm_question, wallet_question
from wellets_cli.util import make_headers, pp
from wellets_cli.validator import (
    AndValidator,
    EmptyInputValidator,
    GreaterThanValidator,
    NumberValidator,
)


@click.group()
def transfer():
    """
    Manage transfers.
    """
    pass


@transfer.command(name="create")
@click.option("--from-wallet-id", type=click.UUID)
@click.option("--to-wallet-id", type=click.UUID)
@click.option("--percentual-fee", type=float)
@click.option("--static-fee", type=float)
@click.option("--value", type=float)
@click.option("-m", "--use-max-balance", type=bool, is_flag=True, default=False)
@click.option("-y", "--yes", is_flag=True, type=bool)
@click.option("--auth-token")
def create_transfer(
    from_wallet_id,
    to_wallet_id,
    percentual_fee,
    static_fee,
    value,
    auth_token,
    use_max_balance,
    yes,
):
    """
    Create a transfer.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)

    from_wallet_id = (
        from_wallet_id
        or wallet_question(message="From wallet", wallets=wallets).execute()
    )

    to_wallet_id = (
        to_wallet_id
        or wallet_question(
            message="To wallet",
            wallets=[wallet for wallet in wallets if wallet.id != from_wallet_id],
        ).execute()
    )

    from_wallet = api.get_wallet(from_wallet_id, headers=headers)

    value = (
        value
        or inquirer.number(
            message=f"Value ({from_wallet.currency.alias})",
            default=from_wallet.balance if use_max_balance else 0,
            float_allowed=True,
            transformer=lambda x: pp(float(x), fixed=False),
            filter=lambda x: float(x),
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=True),
                    GreaterThanValidator(0),
                ]
            ),
        ).execute()
    )

    percentual_fee = (
        percentual_fee
        or inquirer.number(
            message=f"Percentual fee ({from_wallet.currency.alias})",
            float_allowed=True,
            transformer=lambda x: pp(
                float(x) / 100,
                percent=True,
                fixed=False,
                with_symbol=True,
            ),
            filter=lambda x: float(x) / 100,
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=True),
                ]
            ),
        ).execute()
    )

    static_fee = (
        static_fee
        or inquirer.number(
            message=f"Static fee ({from_wallet.currency.alias})",
            float_allowed=True,
            transformer=lambda x: pp(float(x), fixed=False),
            filter=lambda x: float(x),
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=True),
                ]
            ),
        ).execute()
    )

    if not yes and not confirm_question().execute():
        return

    data = {
        "from_wallet_id": from_wallet_id,
        "to_wallet_id": to_wallet_id,
        "percentual_fee": percentual_fee,
        "static_fee": static_fee,
        "value": value,
    }

    transfer = api.create_transfer(
        data=data,
        headers=headers,
    )

    print(transfer.id)
