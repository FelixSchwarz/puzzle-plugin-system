# -*- coding: utf-8 -*-
# The source code in this file is covered by the CC0 v1.0 license.
# full license text: https://creativecommons.org/publicdomain/zero/1.0/
# SPDX-License-Identifier: CC0
# written by: Felix Schwarz (2019)

from pkg_resources import WorkingSet
from pythonic_testcase import *

from schwarz.puzzle_plugins import PluginLoader
from schwarz.puzzle_plugins.lib import AttrDict


class PluginLoaderTest(PythonicTestCase):
    def test_passes_plugin_context_for_init_and_terminate(self):
        _plugin_data = {}
        def _fake_init(context):
            context['key'] = 42
            _plugin_data['init_context'] = context
        fake_plugin = AttrDict({
            'id': 'fake-id',
            'initialize': _fake_init,
            'terminate': lambda context: _plugin_data.setdefault('terminate_context', context),
        })
        working_set = WorkingSet(entries=())
        loader = PluginLoader('invalid', enabled_plugins=(), working_set=working_set)
        loader.activated_plugins[fake_plugin.id] = fake_plugin
        # fake initialization so we can avoid the setuptools entry point
        # machinery (prevent test pollution)
        loader._initialized = True

        loader.initialize_plugins()
        assert_contains('init_context', _plugin_data)
        init_context = _plugin_data['init_context']
        assert_equals({'key': 42}, init_context)

        loader.terminate_plugin(fake_plugin.id)
        assert_contains('terminate_context', _plugin_data)
        assert_equals(id(init_context), id(_plugin_data['terminate_context']),
            message='ensure that the same context is passed to terminate so the plugin can preserve state there')
