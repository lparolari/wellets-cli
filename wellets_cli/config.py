from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="WELLETS",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    env_switcher="WELLETS_ENV",
    validators=[
        Validator("api_url", required=True),
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
