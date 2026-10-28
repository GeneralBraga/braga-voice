import os

import pytest

from braga_voice.config import save_local_provider_config


def test_provider_config_is_private_and_does_not_echo_key(tmp_path) -> None:
    env_path = tmp_path / ".env"
    key = "sk_" + "1234567890abcdefghijkl"
    result = save_local_provider_config(key, "voice_example_01", env_path=env_path)

    assert result == env_path
    assert env_path.stat().st_mode & 0o777 == 0o600
    assert f"ELEVENLABS_API_KEY={key}" in env_path.read_text(encoding="utf-8")
    assert os.environ["ELEVENLABS_API_KEY"] == key


@pytest.mark.parametrize("value", ["", "not-a-key", "sk_short", "sk_valid_but\nmultiline_value"])
def test_provider_config_rejects_invalid_keys(tmp_path, value: str) -> None:
    with pytest.raises(ValueError):
        save_local_provider_config(value, env_path=tmp_path / ".env")
