# The source code in this file is covered by the MIT license.
# full license text: https://spdx.org/licenses/MIT.html
# SPDX-License-Identifier: MIT
# written by: Felix Schwarz (2020, 2024)

from unittest.mock import MagicMock

import pytest

from schwarz.puzzle_plugins.signal_registry import (connect_signals,
    SignalRegistry)


def test_call_plugin():
    registry = SignalRegistry()
    # return None if no plugin did subscribe for the signal
    assert registry.call_plugin('foo', signal_kwargs={'a': 137}) is None

    plugin = lambda sender, a: (a+1)
    connect_signals({'foo': plugin}, registry.namespace)
    assert registry.call_plugin('foo', signal_kwargs={'a': 137}) == 138

    plugin2 = lambda sender, a: (a+5)
    connect_signals({'foo': plugin2}, registry.namespace)
    # return None if multiple receivers are subscribed
    assert registry.call_plugin('foo', signal_kwargs={'a': 137}) is None


def test_call_plugins():
    registry = SignalRegistry()

    # only one plugin returns a value which is the final return value
    plugin = MagicMock(return_value=None, spec={})
    connect_signals({'foo': plugin}, registry.namespace)
    plugin2 = lambda sender, a: (a+1)
    connect_signals({'foo': plugin2}, registry.namespace)
    result = registry.call_plugins('foo', signal_kwargs={'a': 137}, expect_single_result=True)
    assert result == 138
    plugin.assert_called_once_with(None, a=137)

    # ability to return values from all plugins
    plugin3 = MagicMock(side_effect=lambda sender, a: (a-1), spec={})
    connect_signals({'foo': plugin3}, registry.namespace)
    with pytest.raises(ValueError):  # multiple receivers which return values
        registry.call_plugins('foo', signal_kwargs={'a': 127}, expect_single_result=True)
    assert plugin.call_count == 2
    plugin3.assert_called_once_with(None, a=127)

    results = registry.call_plugins('foo', signal_kwargs={'a': 125}, expect_single_result=False)
    assert len(results) == 3
    assert {i[1] for i in results} == {124, 126, None}
    assert plugin.call_count == 3
    assert plugin3.call_count == 2
