# The source code in this file is covered by the MIT license.
# full license text: https://spdx.org/licenses/MIT.html
# SPDX-License-Identifier: MIT
# written by: Felix Schwarz (2019)

from dotmap import DotMap

from schwarz.puzzle_plugins import PluginLoader


class StaticDotMap(DotMap):
    def __init__(self, *args, **kwargs):
        # DotMap uses multiple inheritance so we can not just pass the parameter
        # to `super(...).__init__()`
        kwargs['_dynamic'] = False
        super(StaticDotMap, self).__init__(*args, **kwargs)


def test_passes_plugin_context_for_init_and_terminate():
    _plugin_data = {}
    def _fake_init(context):
        context['key'] = 42
        _plugin_data['init_context'] = context
    fake_plugin = StaticDotMap({
        'id': 'fake-id',
        'initialize': _fake_init,
        'terminate': lambda context: _plugin_data.setdefault('terminate_context', context),
    })
    loader = PluginLoader('invalid', enabled_plugins=())
    loader.activated_plugins[fake_plugin.id] = fake_plugin
    # fake initialization so we can avoid the setuptools entry point
    # machinery (prevent test pollution)
    loader._initialized = True

    loader.initialize_plugins()
    assert 'init_context' in _plugin_data
    init_context = _plugin_data['init_context']
    assert init_context == {'key': 42}

    loader.terminate_plugin(fake_plugin.id)
    assert 'terminate_context' in _plugin_data
    assert id(_plugin_data['terminate_context']) == id(init_context), \
        'ensure that the same context is passed to terminate so the plugin can preserve state there'
