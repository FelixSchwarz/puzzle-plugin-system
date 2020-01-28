# -*- coding: utf-8 -*-
# The source code in this file is covered by the CC0 v1.0 license.
# full license text: https://creativecommons.org/publicdomain/zero/1.0/
# SPDX-License-Identifier: CC0
# written by: Felix Schwarz (2019)

from blinker import Namespace


__all__ = [
    'connect_signals',
    'disconnect_signals',
    'SignalRegistry',
]

def connect_signals(signal_map, signal_registry):
    connected_signals = []
    for signal_name, signal_handler in signal_map.items():
        signal = signal_registry.signal(signal_name)
        signal.connect(signal_handler)
        ref_item = (signal_name, signal_handler)
        connected_signals.append(ref_item)
    return connected_signals

def disconnect_signals(connected_signals, signal_registry):
    for signal_name, signal_handler in connected_signals:
        signal = signal_registry.signal(signal_name)
        signal.disconnect(signal_handler)


class SignalRegistry(object):
    def __init__(self, blinker_namespace=None):
        if blinker_namespace is None:
            blinker_namespace = Namespace()
        self.namespace = blinker_namespace

    @property
    def signal(self):
        return self.namespace.signal

    def connect(self, signal_name, handler):
        signal = self.signal(signal_name)
        signal.connect(handler)

    def disconnect(self, signal_name, handler):
        signal = self.signal(signal_name)
        signal.disconnect(handler)

    def has_receivers(self, signal_name):
        signal_ = self.signal(signal_name)
        nr_receivers = len(signal_.receivers)
        return (nr_receivers > 0)

    def call_plugin(self, signal_name, *, log=None, sender=None, signal_kwargs=None):
        if not self.has_receivers(signal_name):
            if log:
                log.warning('no receivers for signal %r', signal_name)
            return None
        signal_ = self.signal(signal_name)
        nr_receivers = len(signal_.receivers)
        has_multiple_receivers = nr_receivers > 1
        if has_multiple_receivers:
            if log:
                log.warning('%d receivers for signal %r', nr_receivers, signal_name)
            return None

        if signal_kwargs is None:
            signal_kwargs = {}
        sender = (sender,) if sender else ()
        signal_results = signal_.send(*sender, **signal_kwargs)
        if len(signal_results) != 1:
            raise ValueError('multiple results returned after emitting signal %r' % signal_name)

        receiver, receiver_result = signal_results[0]
        return receiver_result

    def send(self, signal_name, *, sender=None, signal_kwargs=None):
        signal_ = self.signal(signal_name)
        sender = (sender,) if sender else ()
        if signal_kwargs is None:
            signal_kwargs = {}
        signal_.send(*sender, **signal_kwargs)

