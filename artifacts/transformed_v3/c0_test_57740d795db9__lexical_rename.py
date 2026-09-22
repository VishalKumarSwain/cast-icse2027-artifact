from optparse import OptionParser
import ConfigParser
import sys

class PerHostValue(object):
    """
    Default class for 'per-host' values.
    """

    def __init__(self, default, file_path):
        self.default = default
        self.file_path = file_path

class PerHostConfig(object):
    """
    Helper class for optparse.OptionParser use by pypelines.
    """

    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name

    def process_overrides(self, parser, overrides):
        for opt, value in overrides.iteritems():
            for section in ('Defaults', self.pipeline_name):
                config_renamed = ConfigParser.SafeConfigParser()
                for file_path in (
                    '/etc/pypeline/{}.ini'.format(self.pipeline_name),
                    '~/.pypeline/{}.ini'.format(self.pipeline_name)
                ):
                    with open(file_path) as f:
                        config_renamed.readfp(f)
                    if opt in config_renamed.options(section):
                        overrides[opt] = config_renamed.get(section, opt)

        for opt, value in overrides.iteritems():
            if isinstance(value, PerHostValue):
                value.value = self._read_ini_value(value.file_path, opt)

        return overrides

    def parse_args(self, parser, argv):
        overrides = {}

        for arg in argv:
            if arg.startswith('--'):
                option, value = arg.split('=', 1)
                overrides[option] = value

        overrides = self.process_overrides(parser, overrides)

        for opt, value in overrides.iteritems():
            setattr(parser.values, opt.replace('-', '_'), value)

        config_renamed, args = parser.parse_args(argv)

        for opt, value in overrides.iteritems():
            if isinstance(value, PerHostValue):
                # Write config file with per-host value if necessary
                if hasattr(parser.values, opt) and parser.values[opt] != value.value:
                    self._write_ini_value(value.file_path, opt, parser.values[opt])

        return config_renamed, args

    def _read_ini_value(self, file_path, opt):
        """
        Reads an option value from the given configuration file.
        """
        config_renamed = ConfigParser.SafeConfigParser()
        with open(file_path) as f:
            config_renamed.readfp(f)
        if opt in config_renamed.options('Defaults'):
            return config_renamed.get('Defaults', opt)
        return None

    def _write_ini_value(self, file_path, opt, value):
        """
        Writes an option value to the given configuration file.
        """
        config_renamed = ConfigParser.SafeConfigParser()
        if not os.path.exists(file_path):
            config_renamed.add_section('Defaults')
        config_renamed.set('Defaults', opt, value)
        with open(file_path, 'w') as f:
            config_renamed.write(f)
