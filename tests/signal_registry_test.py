# -*- coding: utf-8 -*-
# The source code in this file is covered by the CC0 v1.0 license.
# full license text: https://creativecommons.org/publicdomain/zero/1.0/
# SPDX-License-Identifier: CC0
# written by: Felix Schwarz (2020)

from pythonic_testcase import *

from schwarz.puzzle_plugins.signal_registry import (connect_signals,
    SignalRegistry)


class SignalRegistryTest(PythonicTestCase):
    def test_call_plugin(self):
        registry = SignalRegistry()
        assert_none(registry.call_plugin('foo', signal_kwargs={'a': 137}),
            message='return None if no plugin did subscribe for the signal')

        plugin = lambda sender, a: (a+1)
        _signals = connect_signals({'foo': plugin}, registry.namespace)
        assert_equals(138, registry.call_plugin('foo', signal_kwargs={'a': 137}))

        plugin2 = lambda sender, a: (a+5)
        _signals2 = connect_signals({'foo': plugin2}, registry.namespace)
        assert_none(registry.call_plugin('foo', signal_kwargs={'a': 137}),
            message='return None if multiple receivers are subscribed')

