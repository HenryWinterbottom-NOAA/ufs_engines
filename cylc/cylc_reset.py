# =========================================================================

# Script: scripts/cylc_reset.py

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

   cylc_reset.py

Description
-----------

   This script contains a function interface to reset tasks within a
   running Cylc workflow suites.

Classes
-------

   CylcTaskReset()

       This is the base-class object for resetting UFS-RNR Cylc
       workflow tasks to a specified state.

Functions
---------

   main()

       This is the driver-level method to invoke the tasks within this
       script.

Requirements
------------

- ufs_pytils; https://github.com/HenryWinterbottom-NOAA/ufs_pyutils

Author(s)
---------

   Henry R. Winterbottom; 03 January 2023

History
-------

   2023-01-03: Henry Winterbottom -- Initial implementation.

"""

# ----

import os
import time

from confs.yaml_interface import YAML
from cylc import reset_tasks
from cylc.exceptions import CylcEngineError
from schema import Optional
from tools import datetime_interface
from tools import parser_interface
from utils.arguments_interface import Arguments
from utils.error_interface import msg_except_handle
from utils.logger_interface import Logger

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcTaskReset:
    """
    Description
    -----------

    This is the base-class object for resetting UFS-RNR Cylc workflow
    tasks to a specified state.

    """

    @classmethod
    def __init__(cls, options_obj: object):
        """
        Description
        -----------

        Creates a new CylcTaskReset object.

        """

        # Define the base-class attributes.
        self = cls
        self.options_obj = options_obj
        self.logger = Logger()

        self.parser.add_argument('-c', '--cycle', help='The UFS-RNR experiment '
                                 'forecast cycle formatted as (assuming the UNIX '
                                 'POSIX convention) %Y%m%d%H%M%S.', default=None)
        self.parser.add_argument('-d', '--depends', help='The UFS-RNR experiment '
                                 'YAML-formatted file containing the downstream '
                                 'UFS-RNR task dependencies', default=None)
        self.parser.add_argument('-s', '--status', help='The state for which to '
                                 'to reset the respective Cylc task and the respective '
                                 'dependent tasks to.', default=None)
        self.parser.add_argument('-t', '--task', help='The Cylc failed task.',
                                 default=None)
        self.parser.add_argument('-y', '--yaml', help='The UFS-RNR experiment YAML-'
                                 'formatted file containing the user experiment '
                                 'configuration.', default=None)
        self.cyclestr_frmt = '%Y%m%d%H%M%S'
        self.cylcstr_frmt = '%Y%m%dT%H%MZ'

    def build_exptobj(self) -> None:
        """
        Description
        -----------

        This method builds the base-class attribute expt_obj which
        contains the running Cylc workflow attributes assigned by the
        user-specified command line arguments.

        """

        # Collect and build the Cylc attribute bjects.
        self.expt_obj = parser_interface.object_define()
        self.yaml_obj = YAML().read_yaml(yaml_file=self.opts_obj.yaml,
                                         return_obj=True)

        # Check that all mandatory attributes have been provided;
        # proceed accordingly.
        expt_mand_attr_list = ["cycle", "experiment_name", "status"]

        for expt_attr in expt_mand_attr_list:
            value = parser_interface.object_getattr(
                object_in=self.yaml_obj, key=expt_attr, force=True)
            if value is None:
                msg = (f"The attribute {expt_attr} is either NoneType or has "
                       "not been specified using the command line attributes. "
                       "Aborting!!!")
                error(msg=msg)

            self.expt_obj = parser_interface.object_setattr(
                object_in=self.expt_obj, key=expt_attr, value=value)

        # Check the keyword arguments, if any, specified via the
        # command line attributes; proceed accordingly.
        task_depends_list = [self.opts_obj.task]
        if self.opts_obj.depends is not None:

            # Collect the respective task dependencies, if any, using
            # the command line attribute information; proceed
            # accordingly.
            depends_obj = YAML().read_yaml(yaml_file=self.opts_obj.depends,
                                           return_obj=True)

            try:
                depends_list = parser_interface.object_getattr(
                    object_in=depends_obj, key=expt_attr)

                for item in depends_list:
                    task_depends_list.append(item)

            except AttributeError:
                msg = ("Dependencies have not be specified in the YAML-formatted "
                       f"Cylc task dependency file {self.opts_obj.depends}; the specified "
                       f"task {self.opts_obj.task} will only be reset.")
                self.logger.warn(msg=msg)

        # Compile a list of tasks to be reset.
        task_list = []

        for item in task_depends_list:
            out_frmttyp = f"{item}.{timestamp_interface.GLOBAL}"
            task_name = datetime_interface.datestrupdate(
                datestr=self.opts_obj.cycle, in_frmttyp=timestamp_interface.GLOBAL,
                out_frmttype=out_frmttyp)
            msg = f"The Cylc task {task_name} will be reset to {self.opts_obj.status}."
            self.logger.warn(msg=msg)

            task_list.append(task_name)

        self.expt_obj = parser_interface.object_setattr(
            object_in=self.expt_obj, key="tasks", value=task_list)

    def build_optobj(self) -> None:
        """
        Description
        -----------

        This method builds the base-class attribute opts_obj which
        contains the user specified command line arguments.

        """

        # Define the base-class attributes using the mandatory command
        # line attributes; proceed accordingly.
        mand_args_list = ["cycle", "status", "task", "yaml"]

        self.opts_obj = parser_interface.object_define()
        for item in mand_args_list:
            value = parser_interface.object_getattr(
                object_in=self.options_obj, key=item, force=Tru)
            if value is None:
                msg = (f"The mandatory argument {item} cannot be NoneType. "
                       "Aborting!!!")
                error(msg=msg)
            self.opts_obj = parser_interface.object_setattr(
                object_in=self.opts_obj, key=item, value=value)

        # Define the base-class attribute(s) using the optional
        # command line arguments.
        opt_args_list = ["depends"]

        for item in opt_args_list:
            value = parser_interface.object_getattr(
                object_in=self.options_obj, key=item, force=Tru)
            if value is None:
                msg = (f"The optional command line argument {item} has not "
                       "been specified.")
                self.logger.warn(msg=msg)
            self.opts_obj = parser_interface.object_setattr(
                object_in=self.opts_obj, key=item, value=value)

    def reset_cylctask(self):
        """
        Description
        -----------

        This method resets the user-specified Cylc workflow tasks for
        the respective UFS-RNR experiment.

        """

        # STOPPED HERE

        kwargs = {'yaml_obj': self.yaml_obj, 'expt_obj': self.expt_obj}
        reset_task = cylcutil.cylc_interface.CylcResetTasks(**kwargs)
        reset_task.run()

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Collects the user specified command line argument(s).

        (2) Collects the UFS-RNR Cylc workflow attributes from both
            the command line specified arguments as well as the
            YAML-formatted experiment file,

        (3) Resets the state for the specified UFS-RNR Cylc workflow
            tasks.

        """
        msg = ('Application %s beginning.' % os.path.basename(__file__))
        self.logger.info(msg=msg)
        self.build_optobj()
        self.build_exptobj()
        self.reset_cylctask()
        msg = ('Application %s completed.' % os.path.basename(__file__))
        self.logger.info(msg=msg)


# ----

@msg_except_handle(CylcEngineError)
def error(msg: str) -> None:
    """
    Description
    -----------

    This function is the exception handler for the respective module.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """

# ----


def main() -> None:
    """
    Description
    -----------

    This is the driver-level method to invoke the tasks within this
    script.

    """
    cylcreset = CylcTaskReset()
    cylcreset.run()

# ----


if __name__ == '__main__':
    os.environ['HOMErnr'] = os.path.dirname(os.getcwd())
    ush_path = os.path.join(os.getcwd(), 'ush')
    if os.path.exists(ush_path):
        sys.path.append(ush_path)
    else:
        msg = ('The Cylc override script must be launched beneath the UFS-RNR '
               'cylc path; the respective UFS-RNR Cylc libraries/modules '
               'cannot be loaded otherwise. Aborting!!!')
        raise EnvironmentError(msg=msg)
    import ush
    from ush import cylcutil
    main()
