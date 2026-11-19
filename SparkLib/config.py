import configparser as cparser
import os
import re
from codecs import open as codecs_open
from enum import Enum
from string import Template


__all__ = ['parse_config']

_USERNAME_RE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.@-]*$')


def _current_user():
    user = os.environ.get('USER')
    if not user or not _USERNAME_RE.match(user) or '..' in user:
        raise ValueError('USER environment variable is missing or invalid: {!r}'.format(user))
    return user


def parse_config(filename_or_template):
    """ Returns config dictionary for SparkContext initialization
    based on the provided template of config file.

    Parameters
    ----------
    filename_or_template : str or Enum with str values
        Full name of the config file.

    Returns
    -------
    dict
        Dictionary of config parameters. ``${USER}`` placeholders in values
        are replaced with the current user so per-user paths (drivers,
        native libraries, keytab) never point at another user's workspace.

    """

    filename = filename_or_template.value if isinstance(filename_or_template, Enum) else filename_or_template

    config = cparser.ConfigParser()

    config.read_file(codecs_open(filename, 'r', 'utf8'))

    substitutions = None
    options_dict = {}
    for section in config.sections():
        for option in config.options(section):
            value = config.get(section, option)
            if '$' in value:
                if substitutions is None:
                    substitutions = {'USER': _current_user()}
                value = Template(value).substitute(substitutions)
            options_dict[option] = value

    return options_dict
