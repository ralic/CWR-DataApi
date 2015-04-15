# -*- coding: utf-8 -*-

import pyparsing as pp

from cwr.grammar.field import special
from cwr.group import Group
from cwr.transmission import Transmission
from data.accessor import CWRConfiguration
from cwr.grammar.factory.field import DefaultFieldTerminalRuleFactory
from data.accessor import CWRTables
from cwr.grammar.factory.record import RecordRuleDecorator
from cwr.grammar.factory.rule import DefaultRuleFactory


"""
CWR file grammar.

This contains rules for the internal structure of a CWR file.

This have been created from the BNF description included in the CWR specification.
"""

__author__ = 'Bernardo Martínez Garrido'
__license__ = 'MIT'
__status__ = 'Development'
_config = CWRConfiguration()

_data = _config.load_field_config('table')
_data.update(_config.load_field_config('common'))

_factory_field = DefaultFieldTerminalRuleFactory(_data, CWRTables())

_rules = _config.load_transaction_config('common')
_rules.update(_config.load_record_config('common'))
_rules.update(_config.load_group_config('common'))

_decorators = {'transaction': RecordRuleDecorator(_factory_field), 'record': RecordRuleDecorator(_factory_field)}
_group_rule_factory = DefaultRuleFactory(_rules, _factory_field, _decorators)

"""
Fields.
"""

group_transactions = _group_rule_factory.get_rule('transactions')

group_info = _group_rule_factory.get_rule('group_header') + \
             group_transactions + \
             _group_rule_factory.get_rule('group_trailer')

transmission_groups = pp.OneOrMore(group_info)
transmission_groups = transmission_groups.setName('Transmission Groups').setResultsName('groups')

"""
Rules.
"""

# File rule
cwr_transmission = _group_rule_factory.get_rule('transmission_header') + \
                   transmission_groups + \
                   _group_rule_factory.get_rule('transmission_trailer') + \
                   pp.ZeroOrMore(special.lineEnd)

"""
Parsing actions for the patterns.
"""

cwr_transmission.setParseAction(lambda a: _to_transmission(a))

group_info.setParseAction(lambda a: _to_group(a))

"""
Parsing methods.

These are the methods which transform nodes into instances of classes.
"""


def _to_transmission(parsed):
    """
    Transforms the final parsing result into a Transmission instance.

    :param parsed: result of parsing a Transmission
    :return: a Transmission created from the parsed record
    """
    return Transmission(parsed.transmission_header, parsed.transmission_trailer, parsed.groups)


def _to_group(parsed):
    """
    Transforms the final parsing result into a TransactionGroup instance.

    :param parsed: result of parsing a Transactions Group
    :return: a TransactionGroup created from the parsed record
    """
    return Group(parsed.group_header, parsed.group_trailer, parsed.transactions)