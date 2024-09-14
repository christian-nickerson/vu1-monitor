import os

from dynaconf import Dynaconf, Validator  # type: ignore

current_directory = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    envvar_prefix="VU1",
    settings_files=["settings.toml", ".secrets.toml"],
    root_path=current_directory,
    environments=True,
    env_switcher="VU1_ENV",
    validators=[Validator("KEY", default="cTpAWYuRpA2zx75Yh961Cg")],  # default key provided by VU-server
)
