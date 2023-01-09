# =========================================================================

# Module: ush/cylc/reset_tasks.py

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

    reset_tasks.py

Description
-----------

    This module contains the base-class object to allow interactive
    resets of Cylc tasks within a running workflow suite.

Classes
-------

    CylcResetTasks(yaml_obj, expt_obj)

        This is the base-class object which resets the state of
        specified tasks for a running Cylc suite; it is a sub-class of
        CylcEngine.

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications contained in
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Requirements
------------

- cylc-flow; https://github.com/cylc/cylc-flow (49a1683)

Author(s)
---------

    Henry R. Winterbottom; 02 January 2023

History
-------

    2023-01-02: Henry Winterbottom -- Initial implementation.

"""

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

import os

from schema import Optional, Or

from cylc import CylcEngine
from cylc.launcher import CylcLauncher
from tools import parser_interface
from utils import schema_interface

# ----


class CylcResetTasks(CylcEngine):
    """
    Description
    -----------

    This is the base-class object which resets the state of specified
    tasks for a running Cylc suite; it is a sub-class of CylcEngine.

    Parameters
    ----------

    yaml_obj: object

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.

    expt_obj: object

        A Python object containing the experiment attributes required
        to reset the respective experiment Cylc workflow tasks; this
        includes the user-specified state to which to reset and the
        respective tasks for which the state is to be reset.

    """

    def __init__(self, options_obj: object):
        """
        Description
        -----------

        Creates a new CylcResetTasks object.

        """

        # Define the base-class attributes.
        self.options_obj = options_obj
        launcher_cls_schema = CylcLauncher(
            yaml_file=options_obj.yaml_file).cls_schema

        super().__init__(yaml_file=self.options_obj.yaml_file,
                         cls_schema=launcher_cls_schema
                         )

        # Define and valid the options for the Cylc task reset
        # attributes.
        reset_cls_schema = {'cycle': Or(str, int),
                            'status': str,
                            'task': str,
                            'yaml_file': str,
                            Optional('depends'): str
                            }

        reset_dict = parser_interface.object_todict(
            object_in=self.options_obj)

        schema_interface.validate_opts(
            cls_schema=reset_cls_schema, cls_opts=reset_dict)

        # Define the working directory for the respective Cylc
        # application/experiment.
        self.run_dir = os.path.join(
            self.yaml_obj.CYLCworkpath, self.yaml_obj.CYLCexptname, "cylc"
        )
        msg = (
            "The Cylc application/experiment task status reset will be "
            f"executed from path {self.run_dir}."
        )
        self.logger.info(msg=msg)

    def reset_suite(self) -> None:
        """
        Description
        -----------

        This method resets the tasks within the specified Cylc suite
        for the respective experiment.

        """

        # Define the file paths for the standard output and standard
        # error.
        errlog = os.path.join(
            self.run_dir, f"cylc_reset.{self.options_obj.cycle}.err")
        outlog = os.path.join(
            self.run_dir, f"cylc_reset.{self.options_obj.cycle}.out")

        # Define the subprocess command string.
        cmd = [
            "reset",
            f"--state={self.options_obj.status}",
            self.yaml_obj.CYLCexptname,
        ]

        for task in self.options.task:
            cmd.append(task)

        # Run the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = (
                f"The resetting of experiment {self.yaml_obj.CYLCexptname} "
                "task(s) {0} was successful.".format(
                    ", ".join(self.expt_obj.tasks))
            )
            self.logger.info(msg=msg)

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Resets the tasks within the specified Cylc suite for the
            respective experiment.

        """

        # Reset the specified Cylc experiment tasks.
        self.reset_suite()
