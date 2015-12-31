#!/usr/bin/env python
# coding=utf-8

import os
import argparse

from config.settings import VERSION

VERSION_INFO = 'IQIYI&PPS Security BkScanner Version:%s, by BlackYe' % VERSION

INDENT = ' ' * 2
USAGE = os.linesep.join([
    '',
    '%seg1: python main.py --target ' % INDENT,
    ])


def parse(args=None):
    parser = argparse.ArgumentParser(
        usage=USAGE, formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        '-h', '--help', action='help',
        help='Show this help message and exit'
    )
    parser.add_argument('-V', '--version', action='version',
                        version=VERSION_INFO)
    parser.add_argument(
        '-t', '--target', dest='target', required=True,
        help=_format_help('Target domain/rootdomain/ip')
    )
    available_plugins = PluginController.get_available_plugins().keys()
    parser.add_argument(
        '-p', '--plugins', metavar='plugin',
        dest='plugins_specific', nargs='+',
        default=None,
        help=_format_help([
            'Specify the plugins',
            'avaliable: '+' ,'.join(available_plugins),
        ])
    )
    parser.add_argument(
        '-m', '--max_level', dest='max_level', default=4,
        type=int, help=_format_help('Max level to get domain/ip/rootdomain')
    )
    parser.add_argument(
        '-o', '--output_file', dest='output_file',
        help=_format_help('File to ouput result')
    )
    parser.add_argument(
        '--format', dest='output_format', default='csv',
        help=_format_help([
            'The format to output result,',
            'default list:',
            Output.get_output_formats()
        ])
    )
    parser.add_argument(
        '--log_file', dest='log_file',
        help=_format_help('Log file')
    )
    loglevel_choices = {
        1: 'DEBUG',
        2: 'INFO',
        3: 'WARNING',
        4: 'ERROR',
    }
    parser.add_argument(
        '--log_level', dest='log_level',
        type=int, default=1, choices=loglevel_choices,
        help=_format_help('Log level of output to file', loglevel_choices)
    )
    parser.add_argument(
        '--proxy_file', dest='proxy_file',
        help=_format_help([
            'Proxy file, one line one proxy, each line format:',
            'schem,proxy url,',
            'eg:http,http://1.1.1.1:123',
        ])
    )
    parser.add_argument(
        '--verify_proxy', dest='verify_proxy', action='store_true',
        default=False,
        help=_format_help('If verify the proxy list')
    )
    parser.add_argument(
        '--timeout', dest='timeout',
        type=int, default=10,
        help=_format_help('Request timeout')
    )
    args = parser.parse_args(args)
    return args


def _format_help(help_info, choices=None):
    if isinstance(help_info, list):
        help_str_list = help_info[:]
    else:
        help_str_list = [help_info]

    if choices:
        help_str_list.extend([
            '%s%s - %s' % (INDENT, k, v) for k, v in choices.items()
        ])

    help_str_list.append(INDENT + '(DEFAULT: %(default)s)')

    return os.linesep.join(help_str_list)
