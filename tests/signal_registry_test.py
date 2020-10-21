# -*- coding: utf-8 -*-
# The source code in this file is covered by the CC0 v1.0 license.
# full license text: https://creativecommons.org/publicdomain/zero/1.0/
# SPDX-License-Identifier: CC0
# written by: Felix Schwarz (2020)

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from pythonic_testcase import *

from schwarz.puzzle_plugins.signal_registry import (connect_signals,
    SignalRegistry)


class SignalRegistryTest(PythonicTestCase):
    def test_call_plugin(self):
        registry = SignalRegistry()
        assert_none(registry.call_plugin('foo', signal_kwargs={'a': 137}),
            message='return None if no plugin did subscribe for the signal')

        plugin = lambda sender, a: (a+1)
        connect_signals({'foo': plugin}, registry.namespace)
        assert_equals(138, registry.call_plugin('foo', signal_kwargs={'a': 137}))

        plugin2 = lambda sender, a: (a+5)
        connect_signals({'foo': plugin2}, registry.namespace)
        assert_none(registry.call_plugin('foo', signal_kwargs={'a': 137}),
            message='return None if multiple receivers are subscribed')

    def test_call_plugins(self):
        registry = SignalRegistry()

        # only one plugin returns a value which is the final return value
        plugin = MagicMock(return_value=None, spec={})
        connect_signals({'foo': plugin}, registry.namespace)
        plugin2 = lambda sender, a: (a+1)
        connect_signals({'foo': plugin2}, registry.namespace)
        result = registry.call_plugins('foo', signal_kwargs={'a': 137}, expect_single_result=True)
        assert_equals(138, result)
        plugin.assert_called_once_with(None, a=137)

        # ability to return values from all plugins
        plugin3 = MagicMock(side_effect=lambda sender, a: (a-1), spec={})
        connect_signals({'foo': plugin3}, registry.namespace)
        with assert_raises(ValueError, message='multiple receivers which return values'):
            registry.call_plugins('foo', signal_kwargs={'a': 127}, expect_single_result=True)
        assert_equals(2, plugin.call_count)
        plugin3.assert_called_once_with(None, a=127)

        results = registry.call_plugins('foo', signal_kwargs={'a': 125}, expect_single_result=False)
        assert_length(3, results)
        assert_equals({124, 126, None}, {i[1] for i in results})
        assert_equals(3, plugin.call_count)
        assert_equals(2, plugin3.call_count)

