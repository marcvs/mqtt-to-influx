# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# }}}

import os
import sys
import configargparse

        
def parseOptions():
    '''Parse the commandline options'''

    path_of_executable = os.path.realpath(sys.argv[0])
    folder_of_executable = os.path.split(path_of_executable)[0]
    full_name_of_executable = os.path.split(path_of_executable)[1]
    name_of_executable = full_name_of_executable.rstrip('.py')

    config_files = [os.environ['HOME']+'/.config/%s.conf' % name_of_executable,
                    folder_of_executable +'/%s.conf'     % name_of_executable,
                    '/etc/mqtt-to-influx/mqtt-to-influx.conf']

    parser = configargparse.ArgumentParser(
            default_config_files = config_files,
            description=name_of_executable, ignore_unknown_config_file_keys=True)

    parser.add('-c', '--my-config',  is_config_file=True, help='config file path')
    parser.add_argument('--verbose', '-v', action="count", default=0, help='Verbosity')
    parser.add_argument('--debug', '-d', action="count", default=0, help='Debug level')
    parser.add_argument('--influx_db_name',             default="")
    parser.add_argument('--influx_db_user',             default="")
    parser.add_argument('--influx_db_password',         default="")
    parser.add_argument('--influx_db_host',             default="")
    parser.add_argument('--influx_db_port',             default=8086)
    parser.add_argument('--mqtt_user',                  default="")
    parser.add_argument('--mqtt_password',              default="")
    parser.add_argument('--mqtt_host',                  default="")
    parser.add_argument('--mqtt_port',                  default=1883)

    parser.add_argument('--quiet',         '-q'   , default=False, action="store_true")

    # parser.add_argument(dest='access_token'   )

    return parser

# reparse args on import
args = parseOptions().parse_args()
