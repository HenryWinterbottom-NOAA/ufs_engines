# =========================================================================

# Module: ush/cylc/launcher.py

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
    a Cylc workflow suite.

Classes
-------

    CylcLauncher(yaml_obj, suite_path)

        This is the base-class object which registers and launches a
        specified Cylc suite for the respective experiment; it is a
        sub-class of CylcApplication.

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

from cylc import error as __error__
from cylc import CylcEngine

# ----


class CylcLauncher(CylcEngine):
    """
    Description
    -----------

    This is the base-class object which registers and launches a
    specified Cylc suite for the respective experiment; it is a
    sub-class of CylcApplication.

    Parameters
    ----------

    yaml_obj: obj

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.

    suite_path: str

        A Python string specifying the path to the Cylc suite to be
        registered and launched.

    """

    def __init__(self, yaml_obj: object, suite_path: str):
        """
        Description
        -----------

        Creates a new CylcLauncher object.

        """

        # Define the base-class attributes.
        super().__init__(yaml_obj=yaml_obj)
        self.suite_path = suite_path

    def register_suite(self) -> None:
        """
        Description
        -----------

        This method registers the specified Cylc suite; the standard
        out (stdout) and error (stderr) are written to the respective
        experiment cylc sub-directory as cylc_register.out and
        cylc_register.err, respectively.

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
            self.yaml_obj.experiment_name,
            self.suite_path,
            "--run-dir",
            self.run_dir,
        ]

        # Register the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = (
                f"Cylc workflow suite {self.suite_path} registered "
                f"to {self.yaml_obj.experiment_name}."
            )
            self.logger.info(msg=msg)

        if returncode != 0:
            msg = (
                f"Registering Cylc workflow suite {self.suite_path} "
                f"failed! Please refer to {errlog} for more information. "
                "Aborting!!!"
            )
            __error__(msg=msg)

    def run_suite(self) -> None:
        """
        Description
        -----------

        This method launches(e.g., runs) the specified Cylc suite; the
        standard out(stdout) and error(stderr) are written to the
        respective experiment cylc sub-directory as cylc_run.out and
        cylc_run.err, respectively.

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
        cmd = ["run", self.yaml_obj.experiment_name]

        # Run the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = (
                f"Cylc workflow suite {self.suite_path} launched as "
                f"{self.yaml_obj.experiment_name}."
            )
            self.logger.info(msg=msg)

        if returncode != 0:
            msg = (
                f"Launching Cylc workflow suite {self.suite_path} "
                f"failed! Please refer to {errlog} for more information."
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

        # Register the Cylc experiment suite.
        self.register_suite()

        # Launch the Cylc experiment suite.
        self.run_suite()
