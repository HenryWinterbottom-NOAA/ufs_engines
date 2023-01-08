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
Module
------

    launcher.py

Description
-----------

    This module contains the base-class object to register and launch
    a Cylc engine workflow suite.

Classes
-------

    CylcLauncher(yaml_obj, suite_path)

        This is the base-class object which registers and launches a
        specified Cylc engine suite for the respective experiment; it
        is a sub-class of CylcApplication.

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

from schema import Optional

from cylc import CylcEngine
from cylc import error as __error__
from cylc.builder import CylcBuilder

# ----


class CylcLauncher(CylcEngine):
    """
    Description
    -----------

    This is the base-class object which registers and launches a
    specified Cylc suite for the respective experiment; it is a
    sub-class of CylcEngine.

    Parameters
    ----------

    yaml_file: str

        A Python string specifying the path to the YAML-formatted Cylc
        workflow configuration file.

    """

    def __init__(self, yaml_file: str):
        """
        Description
        -----------

        Creates a new CylcLauncher object.

        """

        # Define the base-class attributes.
        cls_schema = {
            "CYLCexptname": str,
            "CYLCinterval": int,
            "CYLCplatform": str,
            "CYLCstart": str,
            "CYLCstop": str,
            "CYLCworkpath": str,
            "EXPTgraph": str,
            "EXPThomepath": str,
            "EXPTruntime": str,
            "EXPTsuite": str,
            "EXPTtasks": str,
            "EXPTworkpath": str,
            Optional("CYLCemail"): str,
            Optional("CYLCmailevents"): str,
            Optional("EXPTenv"): str,
            Optional("EXPTenvironment"): str
        }

        super().__init__(yaml_file=yaml_file, cls_schema=cls_schema)

        # Build the working directory for the respective Cylc
        # application/experiment.
        self.run_dir = os.path.join(self.yaml_obj.CYLCworkpath,
                                    self.yaml_obj.CYLCexptname, 'cylc')
        msg = ("The Cylc application/experiment will be executed from path "
               f"{self.run_dir}."
               )
        self.logger.info(msg=msg)

        self.builder = CylcBuilder(yaml_obj=self.yaml_obj, path=self.run_dir)

    def launch_suite(self, suite_path: str) -> None:
        """
        Description
        -----------

        This method launches(e.g., runs) the specified Cylc suite; the
        standard out(stdout) and error(stderr) are written to the
        respective experiment cylc sub-directory as cylc_run.out and
        cylc_run.err, respectively.

        Parameters
        ----------

        suite_path: str

            A Python string specifying the path to the Cylc engine
            suite.

        Raises
        ------

        CylcError:

            * raised if running/launching the Cylc application suite
              fails.

        """

        # Define the file paths for the standard output and standard
        # error.
        errlog = os.path.join(self.run_dir, "cylc_run.err")
        outlog = os.path.join(self.run_dir, "cylc_run.out")

        # Define the subprocess command string.
        cmd = ["run", self.yaml_obj.CYLCexptname]

        # Run the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = (
                f"Cylc workflow suite {suite_path} launched as "
                f"{self.yaml_obj.CYLCexptname}."
            )
            self.logger.info(msg=msg)

        if returncode != 0:
            msg = (
                f"Launching Cylc workflow suite {suite_path} "
                f"failed! Please refer to {errlog} for more information."
            )
            __error__(msg=msg)

    def register_suite(self, suite_path: str) -> None:
        """
        Description
        -----------

        This method registers the specified Cylc suite; the standard
        out (stdout) and error (stderr) are written to the respective
        experiment cylc sub-directory as cylc_register.out and
        cylc_register.err, respectively.

        Parameters
        ----------

        suite_path: str

            A Python string specifying the path to the Cylc engine
            suite.

        Raises
        ------

        CylcError:

            * raised if registering the Cylc application suite fails.

        """

        # Define the file paths for the standard output and standard
        # error.
        errlog = os.path.join(self.run_dir, "cylc_register.err")
        outlog = os.path.join(self.run_dir, "cylc_register.out")

        # Define the subprocess command string.
        cmd = [
            "register",
            self.yaml_obj.CYLCexptname,
            suite_path,
            "--run-dir",
            self.run_dir
        ]

        # Register the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = (
                f"Cylc workflow suite {suite_path} registered "
                f"to {self.yaml_obj.CYLCexptname}."
            )
            self.logger.info(msg=msg)

        if returncode != 0:
            msg = (
                f"Registering Cylc workflow suite {suite_path} "
                f"failed! Please refer to {errlog} for more information. "
                "Aborting!!!"
            )
            __error__(msg=msg)

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Registers the specified Cylc suite for the respective
            experiment.

        (2) Launches (e.g., runs) the specified Cylc suite for the
            respective experiment.

        """

        # Build the Cylc experiment suite.
        suite_path = self.builder.run()

        # Register the Cylc experiment suite.
        self.register_suite(suite_path=suite_path)

        # Launch the Cylc experiment suite.
        self.launch_suite(suite_path=suite_path)
