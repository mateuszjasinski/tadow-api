from tadow_api.config import Config, set_default_config, get_default_config


def test_config():
    config = Config(
        debug=True,  # Default field,
        custom_field="Test",
    )

    assert config.debug
    assert hasattr(config, "custom_field")
    assert getattr(config, "custom_field") == "Test"


def test_setting_config():
    default_config = get_default_config()
    assert default_config.debug is False

    set_default_config(Config(debug=True))
    assert get_default_config().debug
