import os

from dynaconf import Dynaconf, Validator  # type: ignore

current_directory = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    envvar_prefix="VU1",
    settings_files=["settings.toml", ".secrets.toml"],
    root_path=current_directory,
    environments=True,
    env_switcher="VU1_ENV",
    validators=[
        Validator("name", default="VU1-Monitor"),
        # server
        Validator("server.hostname", default="localhost"),
        Validator("server.port", default=5340),
        Validator("server.logging_level", default="INFO"),
        Validator("server.key", default="cTpAWYuRpA2zx75Yh961Cg"),
        # dials
        Validator("cpu.name", default="CPU"),
        Validator("gpu.name", default="GPU"),
        Validator("gpu.backend", default="nvidia"),
        Validator("memory.name", default="MEMORY"),
        Validator("network.name", default="NETWORK"),
    ],
)
