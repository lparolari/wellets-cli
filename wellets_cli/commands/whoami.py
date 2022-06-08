import click

from wellets_cli.auth import get_email


@click.command()
def whoami():
    email = get_email()

    if email:
        print(email)
    else:
        print("Not logged in")
