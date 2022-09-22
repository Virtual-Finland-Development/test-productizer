import os
from typing import Union


def has_setting(setting_name: str) -> bool:
    return os.getenv(setting_name) is not None


def get_setting(setting_name: str, default_value: Union[str, None] = None) -> str:
    """Get the environment setting or return exception."""
    setting = os.getenv(setting_name)
    if setting is None:
        if default_value is None:
            raise Exception(f"Environment variable {setting_name} is not set.")
        else:
            return default_value
    return setting


def get_bool_setting(setting_name: str, default_value: bool = False) -> bool:
    setting = get_setting(setting_name, "")
    if setting != "":
        return setting.lower() == "true" or setting == "1"
    return False


def if_test_mode():
    return get_setting("PYTEST_CURRENT_TEST", "") != ""
