import unittest

from wellets_cli.config import Config, ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        ConfigManager.add_config(
            Config(
                "foo",
                "bar",
                description="description",
                settable=True,
                server_side=True,
                sensitive=True,
            )
        )
        ConfigManager.add_config(
            Config(
                "cfg",
                "val",
            )
        )

    def tearDown(self):
        ConfigManager.clear()

    def test__keys(self):
        self.assertListEqual(
            ConfigManager.keys(),
            [
                "foo",
                "cfg",
            ],
        )

    def test_keys__server_side(self):
        self.assertListEqual(
            ConfigManager.keys(server_side=True),
            ["foo"],
        )

    def test_keys__settable(self):
        self.assertListEqual(ConfigManager.keys(settable=True), ["foo"])

    def test_has_keys(self):
        self.assertTrue(ConfigManager.has_key("foo"))
        self.assertFalse(ConfigManager.has_key("bar"))

    def test_configs(self):
        self.assertEqual(len(ConfigManager.configs()), 2)

    def test_config(self):
        self.assertEqual(
            ConfigManager.config("foo").value(),
            "bar",
        )
        self.assertIsNone(ConfigManager.config("bar"))

    def test_get(self):
        self.assertEqual(ConfigManager.get("foo", throw=False), "bar")
        self.assertIsNone(ConfigManager.get("bar", throw=False))

    def test_get__raises(self):
        with self.assertRaises(ValueError):
            ConfigManager.get("bar")


class TestConfig(unittest.TestCase):
    def test_create(self):
        config = Config("foo", "bar", description="description")

        self.assertEqual(config.key(), "foo")
        self.assertEqual(config.value(), "bar")
        self.assertEqual(config.description(), "description")
        self.assertEqual(config.is_settable(), False)
        self.assertEqual(config.is_server_side(), False)
        self.assertEqual(config.is_sensitive(), False)

    def test_getter(self):
        def getter(config):
            return f"new value for {config.key()}"

        config = Config("foo", getter=getter)

        self.assertEqual(config.value(), "new value for foo")

    def test_setter(self):
        storage = {}

        def setter(config, value):
            storage[config.key()] = value

        config = Config("foo", setter=setter)

        config.set_value("bar")

        self.assertEqual(storage[config.key()], "bar")
        self.assertIsNone(config.value())

    def test_repr(self):
        config = Config("foo", "bar")

        self.assertEqual(repr(config), "Config(key=foo, value=bar)")

    def test_str(self):
        config = Config("foo", "bar")

        self.assertEqual(str(config), "bar")
