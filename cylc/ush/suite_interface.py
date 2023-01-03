# =========================================================================

# $$$ MODULE DOCUMENTATION BLOCK

# UFS-RNR-cylc :: ush/cylcutils/suite_interface.py

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
Module
------

    suite_interface.py

Description
-----------

    This module contains the Cylc suite version 7.9.x builder object.

Classes
-------

    CylcBuilder(yaml_obj)

        This is the base-class object for all tasks required to build
        a comprehensive suite file for the Cylc workflow manager.

    CylcBuilderError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Error.

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications contained in
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Author(s)
---------

    Henry R. Winterbottom; 03 October 2022

History
-------

    2022-10-03: Henry Winterbottom -- Initial implementation.

"""

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

import collections
import glob
import os

from produtil.error_interface import Error
from produtil.logger_interface import Logger
from tools import datetime_interface
from tools import fileio_interface
from tools import parser_interface

# ----


class CylcBuilder(object):
    """
    Description
    -----------

    This is the base-class object for all tasks required to build a
    comprehensive suite file for the Cylc workflow manager.

    Parameters
    ----------

    yaml_obj: obj

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.

    Raises
    ------

    CylcBuilderError:

        * raised if a mandatory Cylc configuration variable cannot be
          determined from the user experiment configuration.

    """

    def __init__(self, yaml_obj):
        """
        Description
        -----------

        Creates a new CylcBuilder object.

        """

        # Define the base-class attributes.
        self.logger = Logger()
        self.yaml_obj = yaml_obj
        self.cycle_frmttyp = '%Y-%m-%d_%H:%M:%S'
        self.cylc_frmttyp = '%Y%m%dT%H%M%SZ'

        # Define the mandatory attributes required to build the
        # respective Cylc suites.
        cylclist = ['CYLCrnr',
                    'HOMErnr',
                    'NOSCRUBrnr',
                    'WORKrnr',
                    'YAMLrnr',
                    'cycle_interval',
                    'cycle_start',
                    'cycle_stop',
                    'ensmems',
                    'experiment_name',
                    'platform_config',
                    'tasks_config'
                    ]

        # Build the base-class attribute containing the Cylc suite
        # mandatory attributes; proceed accordingly.
        for item in cylclist:

            # Collect the respective attribute from the user
            # experiment configuration.
            if parser_interface.object_hasattr(
                    object_in=self.yaml_obj, key=item):
                value = parser_interface.object_getattr(
                    object_in=self.yaml_obj, key=item)
                msg = (
                    'Experiment configuration: {0} = {1}'.format(item, value))
                self.logger.warn(msg=msg)
                self = parser_interface.object_setattr(
                    object_in=self, key=item, value=value)

            if not parser_interface.object_hasattr(
                    object_in=self.yaml_obj, key=item):
                msg = ('The Cylc configuration variable {0} could not be determined '
                       'from the user experiment configuration. Aborting!!!'
                       .format(item))
                raise CylcBuilderError(msg=msg)

        # Define the optional attributes for the respective Cylc suites.
        cylclist = ['EMAILrnr',
                    'MAILEVENTSrnr'
                    ]

        # Build the base-class attribute in accordance with the
        # attributes specified for the Cylc status mailer within the
        # user experiment configuration; proceed accordingly.
        try:
            if all(parser_interface.object_hasattr(
                    object_in=self.yaml_obj, key=item) for item in cylclist):
                self.mail_event = True
            else:
                self.mail_event = False
        except:
            self.mail_event = False

        # Check whether the user experiment configuration has
        # specified mailer information for the status of Cylc suite
        # tasks; proceed accordingly.
        if self.mail_event:

            # Collect the respective mailer information from the user
            # experiment configuration.
            for item in cylclist:
                value = parser_interface.object_getattr(
                    object_in=self.yaml_obj, key=item)
                msg = (
                    'Experiment configuration: {0} = {1}'.format(item, value))
                self.logger.warn(msg=msg)
                self = parser_interface.object_setattr(
                    object_in=self, key=item, value=value)
            msg = ('Mail notifications for specified Cylc events will be '
                   'triggered.')

        if not self.mail_event:
            for item in cylclist:
                self = parser_interface.object_setattr(
                    object_in=self, key=item, value=None)
            msg = ('Mail notifications for Cylc events will not be triggered.')
        self.logger.warn(msg=msg)

        # Define the Singularity container owner; proceed accordingly.
        item = 'singularity_owner'
        if parser_interface.object_hasattr(
                object_in=self.yaml_obj, key=item):
            value = parser_interface.object_getattr(
                object_in=self.yaml_obj, key=item)

        if not parser_interface.object_hasattr(
                object_in=self.yaml_obj, key=item):
            value = 'nulluser'
        self = parser_interface.object_setattr(
            object_in=self, key=item, value=value)
        msg = ('Experiment configuration: {0} = {1}'.format(item, value))
        self.logger.warn(msg=msg)

        # Define the base-class attributes for the batch-scheduler.
        self.scheduler_obj = parser_interface.object_define()
        self.scheduler_opts = ['slurm']

        # Define the optional configuration file attributes; proceed
        # accordingly.
        self.opts_attrs_obj = parser_interface.object_define()
        cylclist = ['HOMEdata'
                    ]
        for item in cylclist:
            value = parser_interface.object_getattr(
                object_in=self.yaml_obj, key=item, force=True)
            if value is not None:
                msg = (
                    'Experiment configuration: {0} = {1}'.format(item, value))
                self.logger.warn(msg=msg)
                self.opts_attrs_obj = parser_interface.object_setattr(
                    object_in=self.opts_attrs_obj, key=item,
                    value=value)

        # Define the scheduling attributes and the respective default
        # values.
        self.opts_schedule_dict = {'max_active_cycle_points': 3
                                   }

    def build_expt_rc(self):
        """
        Description
        -----------

        This method builds the Cylc suite Jinja2 formatted input file
        experiment.rc; this file contains the directives describing
        the cycling start and stop time, the cycling interval, the
        required paths and experiment name, and the total number of
        ensemble members for the respective experiment.

        """

        # Define timestamps defining the cycling interval.
        cycle_start = datetime_interface.datestrupdate(
            datestr=self.cycle_start, in_frmttyp=self.cycle_frmttyp,
            out_frmttyp=self.cylc_frmttyp)
        cycle_stop = datetime_interface.datestrupdate(
            datestr=self.cycle_stop, in_frmttyp=self.cycle_frmttyp,
            out_frmttyp=self.cylc_frmttyp)
        cycle_interval = ('PT{0}S'.format(self.cycle_interval))

        # Define the Cyle suite attributes and collect the attributes
        # from the user experiment configuration.
        instruct_dict = {'INITIAL_CYCLE_POINT': cycle_start,
                         'FINAL_CYCLE_POINT': cycle_stop,
                         'CYCLE_INTERVAL': cycle_interval,
                         'N_MEMBERS': self.ensmems,
                         'EXPTrnr': self.experiment_name,
                         'SINGULARITY_OWNER': self.singularity_owner
                         }

        envvar_list = ['EMAILrnr',
                       'HOMErnr',
                       'MAILEVENTSrnr',
                       'NOSCRUBrnr',
                       'WORKrnr',
                       'YAMLrnr'
                       ]

        for envvar in envvar_list:
            instruct_dict[envvar] = parser_interface.object_getattr(
                object_in=self, key=envvar, force=True)

        # Append all (if any) optional environment variables to the
        # Cylc suite and establish the run-time environment.
        for envvar in vars(self.opts_attrs_obj):
            value = parser_interface.object_getattr(
                object_in=self.opts_attrs_obj, key=envvar)
            instruct_dict[envvar] = value
            parser_interface.enviro_set(envvar=envvar, value=value)

        # Define the working directory for the Cylc suite
        # configuration; proceed accordingly.
        self.path = os.path.join(self.WORKrnr, self.experiment_name, 'cylc')
        if not os.path.isdir(self.path):
            msg = ('Creating path {0}.'.format(self.path))
            self.logger.info(msg=msg)
            fileio_interface.makedirs(path=self.path)

        # Define all optional Cylc schedule attributes; proceed
        # accordingly.
        for schedule_opt in self.opts_schedule_dict.keys():
            value = parser_interface.object_getattr(
                object_in=self.yaml_obj, key=schedule_opt, force=True)
            if value is None:
                value = parser_interface.dict_key_value(
                    dict_in=self.opts_schedule_dict, key=schedule_opt,
                    no_split=True)
            instruct_dict['{0}'.format(schedule_opt)] = value

        # Define and build the Cylc application Jinja2-formatted
        # experiment.rc file.
        instruct_dict['CYLCrnr'] = self.path
        filename = os.path.join(self.path, 'experiment.rc')
        msg = ('Attempting to build Cylc input file {0}.'.format(filename))
        self.logger.info(msg=msg)

        fileio_interface.write_jinja2(
            jinja2_file=filename, in_dict=instruct_dict)
        msg = ('Creation of Cylc input file {0} succeeded.'.format(filename))
        self.logger.info(msg=msg)

    def build_platform_rc(self):
        """
        Description
        -----------

        This method builds the Cylc suite input file platform.rc; this
        file contains the platform-specific directives for the
        experiment host; the output file is Jinja2 formatted.

        """

        # Build the base-class object specifying the attributes of the
        # batch scheduler.
        for item in self.scheduler_opts:
            self.scheduler_obj = parser_interface.object_setattr(
                object_in=self.scheduler_obj, key=item, value=False)

        # Write the Jinja2-formatted file containing the respective
        # platform attributes; proceed accordingly.
        filename = os.path.join(self.path, 'platform.rc')
        msg = ('Attempting to build Cylc input file {0}.'.format(filename))
        self.logger.info(msg=msg)

        try:

            # Check that the YAML file is valid; proceed accordingly.
            yaml_file = self.platform_config
            if yaml_file is None:
                msg = ('The YAML-formatted file containing the platform attributes '
                       'could not be determined from the command line arguments; '
                       'Aborting!!!')
                raise CylcBuilderError(msg=msg)

            exist = fileio_interface.fileexist(path=yaml_file)
            if not exist:
                msg = ('The YAML-formatted file {0} does not exist. Aborting!!!'
                       .format(yaml_file))
                raise CylcBuilderError(msg=msg)

            # Collect the attributes for the respective platform from
            # the user experiment configuration.
            yaml_obj = fileio_interface.read_yaml(
                yaml_file=yaml_file, return_obj=True)
            platform_obj = fileio_interface.read_yaml(
                yaml_file=self.platform_config, return_obj=True)

            # Check that the batch job scheduler has been defined;
            # proceed accordingly.
            try:
                scheduler = platform_obj.SCHEDULER
            except Exception as error:
                msg = ('The batch system scheduler determination failed with error '
                       '{0}. Aborting!!!'.format(error))
                raise CylcBuilderError(msg=msg)
            for item in self.scheduler_opts:
                if scheduler.lower() == item:
                    self.scheduler_obj = parser_interface.object_setattr(
                        object_in=self.scheduler_obj, key=item, value=True)

            # Define the batch job scheduler attributes; proceed
            # accordingly.
            platform_attrs_list = ['EXEC_RETRIES_COUNT',
                                   'EXEC_RETRIES_INTERVAL_SECONDS'
                                   ]

            # Compare the list contents and proceed accordingly.
            list1 = sorted(platform_attrs_list)
            list2 = sorted(list(set(list(vars(platform_obj).keys())).intersection(
                set(platform_attrs_list))))
            compare = (list1 == list2)

            # Build the instruction(s) attributes.
            instruct_dict = dict()
            for item in set(list(vars(platform_obj).keys())):
                instruct_dict[item] = parser_interface.object_getattr(
                    object_in=platform_obj, key=item)
            if compare:
                for item in platform_attrs_list:
                    instruct_dict[item] = parser_interface.object_getattr(
                        object_in=platform_obj, key=item)
                    exec_retries = "{0}*PT{1}S".format(platform_obj.EXEC_RETRIES_COUNT,
                                                       platform_obj.EXEC_RETRIES_INTERVAL_SECONDS)
            else:
                exec_retries = "0*PT0S"
            instruct_dict['EXEC_RETRIES'] = exec_retries

            # Write the Jinja2-formatted file.
            fileio_interface.write_jinja2(
                jinja2_file=filename, in_dict=instruct_dict)

        except Exception as error:
            msg = ('The construction of Jinja2-formatted file {0} failed '
                   'with error {1}. Aborting!!!'.format(filename, error))
            raise CylcBuilderError(msg=msg)

        msg = ('Creation of Cylc input file {0} succeeded.'.format(filename))
        self.logger.info(msg=msg)

    def build_tasks_rc(self):
        """
        Description
        -----------

        This method builds the Cylc suite ASCII-formatted file
        containing the respective job scheduler directive(s); an
        external file tasks/<task>.task will be created for each
        application specified within the tasks YAML file regardless of
        whether the respective task is a component of the respective
        workflow suite; finally, this method also writes a
        Jinja2-formatted file containing the respective task
        attributes to be referenced by the respective Cylc suite
        applications (when necessary).

        """

        # Define the working directory for the experiment task
        # directives; proceed accordingly.
        directives_path = os.path.join(self.path, 'directives')
        if not os.path.isdir(directives_path):
            msg = ('Creating path {0}.'.format(directives_path))
            self.logger.info(msg=msg)
            fileio_interface.makedirs(path=directives_path)

        # Build scheduler directives for each available task; proceed
        # accordingly.
        try:
            yaml_file = self.tasks_config
            tasks_dict = fileio_interface.read_yaml(yaml_file=yaml_file)

            # Build the respective directives file for each available
            # task.
            instruct_dict = dict()
            for (key, values) in tasks_dict.items():

                # Define and build the file path for the respective
                # task.
                filename = os.path.join(
                    directives_path, '{0}.task'.format(key))
                msg = ('Creating task directives file {0}.'.format(filename))
                self.logger.info(msg=msg)

                # Write the respective task directives to the
                # respective task file.
                with open(filename, 'w') as f:
                    for value in values:
                        if value == 'ntasks':
                            instruct_dict['%s_%s' % (key, value)] = \
                                tasks_dict[key][value]
                        if self.scheduler_obj.slurm:
                            if value == 'cpus-per-task':
                                instruct_dict['%s_nthreads' % key] = \
                                    tasks_dict[key][value]
                        f.write('--%s = %s\n' %
                                ((value, tasks_dict[key][value])))

            # Build the master file containing all available task
            # directives.
            filename = os.path.join(self.path, 'tasks.rc')
            fileio_interface.write_jinja2(
                jinja2_file=filename, in_dict=instruct_dict)
            msg = (
                'Creation of Cylc input file {0} succeeded.'.format(filename))
            self.logger.info(msg=msg)

        except Exception as error:
            msg = ('Defining the available task files failed with error {0}. '
                   'Aborting!!!'.format(error))
            raise CylcBuilderError(msg=msg)

    def configure_cylc(self):
        """
        Description
        -----------

        This method copies the Cylc configuration files to the
        respective experiment location.

        Returns
        -------

        suite_path: str

            A Python string specifying the path to the experiment path
            for the user-specified Cylc suite.

        """

        # Define the path for the Cylc configuration files.
        expt_path = os.path.join(self.WORKrnr, self.experiment_name)

        # Define and copy the required Cylc application files to the
        # specified path.
        configure_file_list = ['environment.rc',
                               'runtime.rc',
                               'suite.rc'
                               ]
        for configure_file in configure_file_list:

            # Attempt to find the respective source file; proceed
            # accordingly.
            filelist = glob.glob(
                '**/{0}'.format(configure_file), recursive=True)
            srcfile = [x for x in filelist if configure_file in x][0]
            if len(srcfile) <= 0:
                msg = ('The configuration file {0} could not be found. '
                       'Aborting!!!'.format(srcfile))
                raise CylcBuilderError(msg=msg)

            # Copy the respective file to the appropriate location.
            srcfile = os.path.join(os.getcwd(), srcfile)
            dstfile = os.path.join(expt_path, 'cylc', configure_file)
            msg = ('Copying file {0} to {1}.'.format(srcfile, dstfile))
            self.logger.info(msg=msg)
            fileio_interface.copyfile(srcfile=srcfile, dstfile=dstfile)

        # If applicable, update the environment suite file.
        envvar_rc_path = os.path.join(expt_path, 'cylc', 'environment.rc')
        f = open(envvar_rc_path, 'a')
        for envvar in vars(self.opts_attrs_obj).keys():
            try:
                value = parser_interface.object_getattr(
                    object_in=self.opts_attrs_obj, key=envvar)
                if isinstance(value, str):
                    f.write('{0} = "{1}"\n'.format(envvar, value))
                else:
                    f.write('{0} = {1}\n'.format(envvar, value))
                msg = ('Writing environment variable {0} as {1} to {2}.'
                       .format(envvar, value, envvar_rc_path))
                self.logger.warn(msg=msg)
            except Exception:
                pass
        f.close()

        # Copy the Cylc graph (i.e., workflow) to the appropriate
        # location.
        srcfile = self.CYLCrnr
        dstfile = os.path.join(expt_path, 'cylc', 'graph.rc')
        msg = ('Copying file {0} to {1}.'.format(srcfile, dstfile))
        self.logger.info(msg=msg)
        fileio_interface.copyfile(srcfile=srcfile, dstfile=dstfile)

        # Define the Cylc application suite path.
        suite_path = os.path.join(expt_path, 'cylc', 'suite.rc')

        return suite_path

    def run(self):
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Builds the Cylc suite experiment.rc input file.

        (2) Builds the Cylc suite platform.rc input file.

        (3) Builds the Cylc suite tasks.rc input file.

        All files are Jinja2-formatted.

        Returns
        -------

        suite_path: str

            A Python string specifying the path to the experiment path
            for the user-specified UFS-RNR Cylc suite.

        """

        # Build each component of the Cylc application suite.
        self.build_expt_rc()
        self.build_platform_rc()
        self.build_tasks_rc()

        # Configure Cylc and define the path to the Cylc application
        # suite.
        suite_path = self.configure_cylc()

        return suite_path

# ----


class CylcBuilderError(Error):
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

        Creates a new CylcBuilderError object.

        """
        super(CylcBuilderError, self).__init__(msg=msg)
