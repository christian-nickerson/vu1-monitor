import os

from dynaconf import Dynaconf

current_directory = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    envvar_prefix="VU1",
    settings_files=["settings.toml", ".secrets.toml"],
    root_path=current_directory,
    environments=True,
    env_switcher="VU1_ENV",
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
