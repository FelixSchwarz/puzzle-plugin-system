# -*- coding: utf-8 -*-
# The source code in this file is covered by the CC0 v1.0 license.
# full license text: https://creativecommons.org/publicdomain/zero/1.0/
# SPDX-License-Identifier: CC0
# written by: Felix Schwarz (2014, 2015, 2019)

from __future__ import division, absolute_import, print_function, unicode_literals

from collections import OrderedDict
import logging

import pkg_resources


__all__ = ['PluginLoader']

class PluginLoader(object):
    def __init__(self, entry_point_name, enabled_plugins=('*',), log=None, working_set=None):
        self.entry_point_name = entry_point_name
        self.enabled_plugins = enabled_plugins
        self.log = log or logging.getLogger(__name__)
        self.working_set = working_set or pkg_resources.working_set
        self.activated_plugins = OrderedDict()
        self._initialized = False

    def init(self):
        self.activated_plugins = OrderedDict()
        # LATER/enhancement: two-pass initialization, gather all requirements,
        # build a directed acyclic graph and perform a topological sort to load
        # all plugins in the right order (in case plugins depend on each other)
        epoints = tuple(self.working_set.iter_entry_points(self.entry_point_name))
        for epoint in epoints:
            plugin_id = epoint.name
            # LATER: check for duplicate plugin id
            if not self.is_plugin_enabled(plugin_id):
                self.log.debug('Skipping plugin %s: not enabled', self._plugin_info(epoint))
                continue
            self.activated_plugins[plugin_id] = self._plugin_from_entry_point(epoint)
            self.log.debug('Plugin loaded: %s', self._plugin_info(epoint))
        self._initialized = True

    def initialize_plugins(self, *args, **kwargs):
        if not self._initialized:
            self.init()
        for plugin in self.activated_plugins.values():
            plugin.initialize(*args, **kwargs)

    def is_plugin_enabled(self, plugin_id):
        return (plugin_id in self.enabled_plugins) or ('*' in self.enabled_plugins)

    def _plugin_info(self, epoint):
        plugin_id = epoint.name
        dist = epoint.dist
        return '%s %s (%r, %s)' % (dist.project_name, dist.version, plugin_id, dist.location)

    def _plugin_from_entry_point(self, epoint):
        # LATER: catch exceptions while loading plugins
        module_or_function = epoint.load()
        if callable(module_or_function):
            plugin = module_or_function()
        else:
            # entry point specification referred to a module. We could
            # check for some kind of "magic" attribute (e.g. module__plugin__)
            # or just tell the plugin manager what to use.
            raise NotImplementedError()
        return plugin

