from tadow_api.config import Config, app_config
from tadow_api import TadowAPI


def test_config():
    config = Config(
        debug=True,  # Default field,
        custom_field="Test",
    )

    assert config.debug
    assert hasattr(config, "custom_field")
    assert getattr(config, "custom_field") == "Test"


def test_setting_config():
    TadowAPI(config=Config(debug=True))
    assert app_config().debug
