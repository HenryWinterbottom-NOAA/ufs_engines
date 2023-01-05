# =========================================================================

# $$$ SCRIPT DOCUMENTATION BLOCK

# UFS-RNR-cylc :: cylc_run.py

# Author: Henry R. Winterbottom

# Email: henry.winterbottom@noaa.gov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the respective public license published by the
# Free Software Foundation and included with the repository within
# which this application is contained.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# =========================================================================

"""
Script
------

    cylc_run.py

Description
-----------

    This script is the driver script for all experiment workflows
    orchestrated by Cylc version 7.9.x.

Classes
-------

    CylcRun()

        This is the base-class object for compiling (e.g., building)
        an experiment Cylc suite and subsequently launching the
        respective experiment Cylc suite.

    CylcRunError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    CylcRunOptions()

        This is the base-class object to parse all user specified
        options passed to the driver level of the script.

Functions
---------

    main()

        This is the driver-level function to invoke the tasks within
        this script.

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications contained in
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Author(s)
---------

    Henry R. Winterbottom; 04 October 2022

History
-------

    2022-10-04: Henry Winterbottom -- Initial implementation.

"""

# ----

import os
import time

from argparse import ArgumentParser
from cylcutil import cylc_interface
from cylcutil import suite_interface
from produtil.error_interface import Error
from produtil.logger_interface import Logger
from tools import fileio_interface
from tools import parser_interface

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

logger = Logger()

# ----


class CylcRun(object):
    """
    Description
    -----------

    This is the base-class object for compiling (e.g., building)
    anexperiment Cylc suite and subsequently launching the respective
    experiment Cylc suite.

    Parameters
    ----------

    opts_obj: obj

        A Python object containing the user command line options.

    Raises
    ------

    CylcRunError:

        * raised if the command line arguments do not specify the
          experiment configuration file.

        * raised if the experiment configuration file does not exist.

    """

    def __init__(self, opts_obj):
        """
        Description
        -----------

        Creates a new CylcRun object.

        """

        # Define the base-class attributes.
        self.logger = Logger()
        yaml_file = parser_interface.object_getattr(
            object_in=opts_obj, key='yaml', force=None)
        if yaml_file is None:
            msg = ('The configuration file could not be determined '
                   'from the user command-line arguments. Aborting!!!')
            raise CylcRunError(msg=msg)
        exist = fileio_interface.fileexist(path=yaml_file)
        if not exist:
            msg = ('The configuration file path {0} does not exist. '
                   'Aborting!!!'.format(yaml_file))
            raise CylcRunError(msg=msg)

        # Define the mandatory run-time environment variables; proceed
        # accordingly.
        yaml_dict = fileio_interface.read_yaml(
            yaml_file=yaml_file)
        envvar_list = ['HOMErnr',
                       'WORKrnr'
                       ]
        for envvar in envvar_list:
            value = parser_interface.dict_key_value(
                dict_in=yaml_dict, key=envvar, force=True,
                no_split=True)
            if value is None:
                msg = ('The environment variable {0} could not be '
                       'determined from the experiment configuration file '
                       '{1}. Aborting!!!'.format(envvar, yaml_file))
                raise CylcRunError(msg=msg)
            parser_interface.enviro_set(envvar=envvar,
                                        value=value)

        # Define the optional run-time environment variables; proceed
        # accordingly.
        envvar_list = ['HOMEdata'
                       ]
        for envvar in envvar_list:
            value = parser_interface.dict_key_value(
                dict_in=yaml_dict, key=envvar, force=True,
                no_split=True)
            if value is not None:
                parser_interface.enviro_set(envvar=envvar,
                                            value=value)

        # Parse the experiment configuration file.
        self.yaml_obj = fileio_interface.read_yaml(
            yaml_file=yaml_file, return_obj=True)

    def build_cylc(self):
        """
        Description
        -----------

        This method builds the respective experiment Cylc suite
        components and defines the base-class attribute suite_path
        which is the filename path for the respective experiment Cylc
        suite.rc (e.g., Cylc suite) file.

        Raises
        ------

        CylcRunError:

            * raised if an exception is encountered while building the
              respective experiment Cylc suite components.

        """

        # Build the experiment Cylc workflow orchestrator suite
        # components; proceed accordingly.
        try:
            builder = suite_interface.CylcBuilder(yaml_obj=self.yaml_obj)
            self.suite_path = builder.run()
        except Exception as error:
            msg = ('Building the respective experiment Cylc suite '
                   'components failed with error {0}. Aborting!!!'
                   .format(error))
            raise CylcRunError(msg=msg)

    def launch_cylc(self):
        """
        Description
        -----------

        This method launches the respective experiment Cylc suite.

        Raises
        ------

        CylcRunError:

            * raised if an exception is encountered while launching
              the respective experiment Cylc suite.

        """

        # Launch the respective Cylc workflow.
        try:
            launcher = cylc_interface.CylcLauncher(
                yaml_obj=self.yaml_obj, suite_path=self.suite_path)
            launcher.run()
        except Exception as error:
            msg = ('Launching the Cylc workflow failed with error {0}. '
                   'Aborting!!!'.format(error))
            raise CylcRunError(msg=msg)

    def run(self):
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Builds the Cylc suite for the respective experiment.

        (2) Launches the Cylc suite for the respective experiment.

        """

        # Build the Cylc suite for the respective experiment.
        self.build_cylc()

        # Launches the Cylc suite for the respective experiment.
        self.launch_cylc()

# ----


class CylcRunError(Error):
    """
    Description
    -----------

    This is the base-class for all exceptions; it is a sub-class of
    Error.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """

    def __init__(self, msg):
        """
        Description
        -----------

        Creates a new CylcRunError object.

        """
        super(CylcRunError, self).__init__(msg=msg)

# ----


class CylcRunOptions(object):
    """
    Description
    -----------

    This is the base-class object to parse all user specified options
    passed to the driver level of the script.

    """

    def __init__(self):
        """
        Description
        -----------

        Creates a new CylcRunOptions object.

        """

        # Collect command line arguments.
        self.parser = ArgumentParser()
        self.parser.add_argument('-y', '--yaml', help='The UFS-RNR experiment YAML-'
                                 'formatted file containing the user experiment '
                                 'configuration.', default=None)

    def run(self):
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Collects the user-specified command line arguments.

        (2) Defines and returns a Python object containing the
            respective command line argument(s).

        Returns
        -------

        opts_obj: obj

            A Python object containing the user command line options.

        Raises
        ------

        CylcRunError:

            * raised if a mandatory command line argument is not
              specified (i.e., is NoneType) upon entry.

        """

        # Build the Python object containing the command line
        # arguments.
        opts_obj = parser_interface.object_define()
        args = self.parser.parse_args()
        args_list = ['yaml']
        for arg in args_list:
            value = parser_interface.object_getattr(
                object_in=args, key=arg, force=True)
            if value is None:
                msg = ('The command line argument {0} cannot be NoneType. '
                       'Aborting!!!'.format(arg))
                raise CylcRunError(msg=msg)
            opts_obj = parser_interface.object_setattr(
                object_in=opts_obj, key=arg, value=value)

        return opts_obj


# ----


def main():
    """
    Description
    -----------

    This is the driver-level function to invoke the tasks within this
    script.

    """
    script_name = os.path.basename(__file__)
    start_time = time.time()
    msg = ('Beginning application {0}.'.format(script_name))
    logger.info(msg=msg)
    options = CylcRunOptions()
    opts_obj = options.run()
    cylcrun = CylcRun(opts_obj=opts_obj)
    cylcrun.run()
    stop_time = time.time()
    msg = ('Completed application {0}.'.format(script_name))
    logger.info(msg=msg)
    total_time = stop_time - start_time
    msg = ('Total Elapsed Time: {0} seconds.'.format(total_time))
    logger.info(msg=msg)

# ----


if __name__ == '__main__':
    main()
