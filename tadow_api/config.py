from typing import Optional


_default_config: Optional["Config"] = None


def set_default_config(config: "Config") -> None:
    """
    Method used to set default config for global usage.
    :param config: Config instance
    """
    global _default_config
    _default_config = config


def get_default_config() -> "Config":
    """
    Return custom instance of config or default.
    :return:
    """
    return _default_config or Config()


class Config:
    """@DynamicAttrs"""

    def __init__(
        self,
        debug: bool = False,
        default_content_type: str = "application/json",
        default_encoding: str = "utf-8",
        **extra_fields,
    ) -> None:
        self.debug = debug
        self.default_content_type = default_content_type
        self.default_encoding = default_encoding

        # Add custom fields to object
        for field, value in extra_fields.items():
            setattr(self, field, value)
