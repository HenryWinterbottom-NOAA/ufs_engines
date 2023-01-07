# =========================================================================

# Module: cylc/launcher.py

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

"""

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

import os

from confs import jinja2_interface
from confs.yaml_interface import YAML
from cylc import error as __error__
from cylc import CylcEngine
from tools import datetime_interface
from tools import fileio_interface
from tools import parser_interface
from utils import timestamp_interface
from utils.logger_interface import Logger

# ----


class CylcBuilder:
    """
    Description
    -----------

    This is the base-class object for all tasks required to build a
    comprehensive suite file for the Cylc workflow manager.

    Parameters
    ----------

    yaml_obj: object

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.



    """

    def __init__(self, yaml_obj: object, path: str):
        """
        Description
        -----------

        Creates a new CylcBuilder object.

        """

        # Define the base-class attributes.
        self.yaml_obj = yaml_obj
        self.path = path
        self.logger = Logger()

        # Build the working directory for the Cylc experiment.
        fileio_interface.dirpath_tree(path=self.path)

        # Define the run-time environment variable attributes; the
        # additional environment variable, relative to the respective
        # experiment, will be collected when build the respective
        # experiment Cylc configuration file.
        self.envvar_list = ["CYLCemail", "CYLCexptname",
                            "CYLCmailevents", "CYLCworkpath"]

    def build_expt_rc(self) -> None:
        """
        Description
        -----------

        This method builds the Cylc suite Jinja2-formatted
        experiment.rc file; this file contains the directives
        describing the cycling start and stop time, the cycling
        interval, and any other environment variables specified within
        the Cylc experiment configurtion attributes.

        """

        # Define the Cylc experiment time attributes.
        cycle_start = datetime_interface.datestrupdate(
            datestr=self.yaml_obj.CYLCstart, in_frmttyp=timestamp_interface.GENERAL,
            out_frmttyp=timestamp_interface.YmdTHMS)
        cycle_stop = datetime_interface.datestrupdate(
            datestr=self.yaml_obj.CYLCstop, in_frmttyp=timestamp_interface.GENERAL,
            out_frmttyp=timestamp_interface.YmdTHMS)
        cycle_interval = f"PT{self.yaml_obj.CYLCinterval}S"

        # Define the experiment configuration attributes; proceed
        # accordingly.
        instruct_dict = {'INITIAL_CYCLE_POINT': cycle_start,
                         'FINAL_CYCLE_POINT': cycle_stop,
                         'CYCLE_INTERVAL': cycle_interval}

        for envvar in self.envvar_list:
            value = parser_interface.object_getattr(
                object_in=self.yaml_obj, key=envvar, force=True)
            if value is None:
                msg = (f"Cylc experiment variable {envvar} has not been specified "
                       "and will not be defined for the respective Cylc experiment."
                       )
                self.logger.warn(msg=msg)

            if value is not None:
                msg = f"Cylc experiment variable {envvar} will be defined as {value}."
                self.logger.info(msg=msg)
                instruct_dict[envvar] = value

        # Check whether the respective Cylc experiment configuration
        # has specified additional run-time environment variables;
        # proceed accordingly.
        env_yaml = parser_interface.object_getattr(
            object_in=self.yaml_obj, key="CYLCenv", force=True)
        if env_yaml is None:
            msg = ("The respective Cylc experiment configuration has not specified "
                   "additional environment variables."
                   )
            self.logger.warn(msg=msg)

        if env_yaml is not None:

            # Check that the YAML-formatted file exists; proceed
            # accordingly.
            exist = fileio_interface.fileexist(path=env_yaml)
            if exist:

                # Parse the YAML-formatted file and proceed accordingly.
                env_dict = YAML().read_yaml(yaml_file=env_yaml)

                for (env_item, _) in env_dict.items():
                    instruct_dict[env_item] = parser_interface.dict_key_value(
                        dict_in=env_dict, key=env_item, no_split=True)

            if not exist:
                msg = (f"The environment variable file {env_yaml} does not exist "
                       "and will not be processed."
                       )
                self.logger.warn(msg=msg)

        # Build the Cylc experiment.rc file for the respective experiment.
        filename = os.path.join(self.path, "experiment.rc")
        msg = f"Building Cylc experiment file {filename}."
        self.logger.info(msg=msg)

        jinja2_interface.write_jinja2(
            jinja2_file=filename, in_dict=instruct_dict)

    def build_platform_rc(self):
        """
        Description
        -----------

        This method builds the Cylc suite input file platform.rc; this
        file contains the platform-specific directives for the UFS-RNR
        experiment host; the output file is Jinja2 formatted.

        """
        for item in self.scheduler_opts:
            setattr(self.scheduler_obj, item, False)
        filename = os.path.join(self.path, 'platform.rc')
        msg = ('Attempting to build Cylc input file %s.' % filename)
        self.logger.info(msg=msg)
        try:
            yaml_file = self.platform_config
            if yaml_file is None:
                msg = ('The YAML-formatted file containing the platform attributes '
                       'could not be determined from the command line arguments; '
                       'Aborting!!!')
                raise self.exception(msg=msg)
            kwargs = {'yaml_file': yaml_file}
            yaml_obj = cylcutil.yaml_interface.read_yaml(**kwargs)
            kwargs = {'yaml_file': self.platform_config}
            platform_obj = cylcutil.yaml_interface.read_yaml(**kwargs)
            try:
                scheduler = platform_obj.SCHEDULER
            except KeyError:
                scheduler = None
            if scheduler is None:
                msg = ('The batch system scheduler could not be determined from '
                       'the user experiment configuration. Aborting!!!')
                raise self.exception(msg=msg)
            for item in self.scheduler_opts:  # NEED TO ADD SCHEDULER TO YAML FILE
                if scheduler.lower() == item:
                    setattr(self.scheduler_obj, item, True)
            instruct_dict = dict()
            for item in platform_obj.attr_list:
                instruct_dict[item] = getattr(platform_obj, item)
            if ('EXEC_RETRIES_COUNT' in platform_obj.attr_list) and \
               ('EXEC_RETRIES_INTERVAL_SECONDS' in platform_obj.attr_list):
                exec_retries = "%s*PT%sS" % (platform_obj.EXEC_RETRIES_COUNT,
                                             platform_obj.EXEC_RETRIES_INTERVAL_SECONDS)
            else:
                exec_retries = "0*PT0S"
            instruct_dict['EXEC_RETRIES'] = exec_retries
            kwargs = {'filename': filename, 'instruct_dict': instruct_dict}
            self.write_jinja2(**kwargs)
        except Exception:
            msg = ('The platform.rc file could not be constructed; Aborting!!!')
            raise self.exception(msg=msg)
        msg = ('Creation of Cylc input file %s succeeded.' % filename)
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
        workflow suite; finally, this method also writes a Jinja2
        formatted file containing the respective task attributes to be
        referenced by the respective Cylc suite applications (when
        necessary).

        """

        # Build the directory tree for the job scheduler directives.
        path = os.path.join(self.path, "directives")
        fileio_interface.dirtree_path(path=path)

        print(self.tasks_config)
        quit()

        try:
            yaml_file = self.tasks_config
            kwargs = {'yaml_file': yaml_file, 'return_dict': True}
            tasks_dict = cylcutil.yaml_interface.read_yaml(**kwargs)
            instruct_dict = dict()
            for (key, values) in tasks_dict.items():
                filename = os.path.join(directives_path, '%s.task' % key)
                msg = ('Creating task directives file %s.' % filename)
                self.logger.info(msg=msg)
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
                                (value, tasks_dict[key][value]))
            filename = os.path.join(self.path, 'tasks.rc')
            kwargs = {'filename': filename, 'instruct_dict': instruct_dict}
            self.write_jinja2(**kwargs)
            msg = ('Creation of Cylc input file %s succeeded.' % filename)
            self.logger.info(msg=msg)
        except Exception:
            msg = ('The task files could not be constructed; Aborting!!!')
            raise self.exception(msg=msg)

    def configure_cylc(self):
        """
        Description
        -----------

        This method copies the UFS-RNR Cylc configuration files to the
        respective experiment location.

        Returns
        -------

        suite_path: str

            A Python string specifying the path to the experiment path
            for the user-specified UFS-RNR Cylc suite.

        """
        expt_path = os.path.join(self.WORKrnr, self.experiment_name)
        configure_file_list = ['environment.rc', 'runtime.rc', 'suite.rc']
        for configure_file in configure_file_list:
            srcfile = os.path.join(self.HOMErnr, 'cylc', 'parm',
                                   configure_file)
            dstfile = os.path.join(expt_path, 'cylc', configure_file)
            shutil.copy(srcfile, dstfile)
        srcfile = self.CYLCrnr
        dstfile = os.path.join(expt_path, 'cylc', 'graph.rc')
        shutil.copy(srcfile, dstfile)
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

        # Build the Cylc experiment suite experiment.rc file.
        self.build_expt_rc()
        self.build_platform_rc()
        self.build_tasks_rc()

        suite_path = self.configure_cylc()
        return suite_path
