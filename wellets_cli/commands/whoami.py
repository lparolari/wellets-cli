import click

from wellets_cli.auth import get_email


@click.command()
def whoami():
    """
    Print the information of current user.
    """
    email = get_email()

    if email:
        print(email)
    else:
        print("Not logged in")
