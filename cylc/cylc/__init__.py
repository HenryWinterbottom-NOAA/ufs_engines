# =========================================================================

# Module: cylc/__init__.py

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

    __init__.py

Description
-----------

    This module contains the base-class object for all Cylc engine
    applications.

Classes
-------

    CylcEngine(yaml_file, cls_schema=None)

        This is the base-class object for all Cylc engine
        applications.

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications from
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Requirements
------------

- cylc-flow; https://github.com/cylc/cylc-flow (49a1683)

Author(s)
---------

    Henry R. Winterbottom; 03 January 2023

History
-------

    2023-01-03: Henry Winterbottom -- Initial implementation.

"""

# ----

# pylint: disable=unused-argument

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

import os
from typing import Tuple

from confs.yaml_interface import YAML
from execute import subprocess_interface
from schema import Optional, Or
from tools import parser_interface, system_interface
from utils.error_interface import msg_except_handle
from utils.logger_interface import Logger
from utils.schema_interface import validate_opts

from cylc.exceptions import CylcEngineError

# ----


class CylcEngine:
    """
    Description
    -----------

    This is the base-class object for all Cylc workflow engine
    applications.

    Parameters
    ----------

    yaml_file: str

        A Python string specifying the path to the YAML-formatted Cylc
        workflow configuration file.

    Keywords
    --------

    cls_schema: dict, optional

        A Python dictionary containing the attributes, collected from
        the YAML-formatted Cylc workflow configuration file (above),
        available to the sub-class.

    """

    def __init__(self, yaml_file: str, cls_schema: dict = None):
        """
        Description
        -----------

        Creates new CylcEngine object.

        """

        # Define the base-class attributes.
        self.yaml_obj = YAML().read_yaml(yaml_file=yaml_file, return_obj=True)
        self.logger = Logger()
        self.get_cylc_app()

        # Check that application has all required and any optional
        # attributes.
        if cls_schema is not None:
            cls_opts = parser_interface.object_todict(object_in=self.yaml_obj)
            validate_opts(cls_schema=cls_schema, cls_opts=cls_opts)

    def get_cylc_app(self) -> None:
        """
        Description
        -----------

        This method checks whether the Cylc application executable is
        loaded within the user run-time environment; if so, the
        base-class attribute cylc_app is defined; if not, a CylcError
        exception is raised.

        Raises
        ------

        CylcEngineError:

            * raised if the cylc application executable path can not
              be determined from the run-time environment.

        """

        # Parse the run-time environment for the Cylc executable;
        # proceed accordingly.
        self.cylc_app = system_interface.get_app_path(app="cylc")

        if self.cylc_app is None:
            msg = (
                "The cylc executable could not be determined for your system; "
                "please check that the appropriate modules are loaded. "
                "Aborting!!!"
            )
            error(msg=msg)

        msg = f"The Cylc application path is {self.cylc_app}."
        self.logger.info(msg=msg)

    def run_task(self, cmd: list, errlog: str = None, outlog: str = None) -> int:
        """
        Description
        -----------

        This method launches the command(s) specified in the commands
        list upon entry.

        Parameters
        ----------

        cmd: list

            A Python list containing the command(s) to be launched.

        Keywords
        --------

        errlog: str, optional

            A Python string specifying the path to the standard error
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        outlog: str, optional

            A Python string specifying the path to the standard output
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        Return
        ------

        returncode: int

            A Python integer specifying the return code provided by
            the subprocess command.

        """

        # Launch the command(s) specified in the commands list.
        returncode = subprocess_interface.run(
            exe=self.cylc_app, job_type="app", args=cmd, errlog=errlog, outlog=outlog
        )

        return returncode


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
