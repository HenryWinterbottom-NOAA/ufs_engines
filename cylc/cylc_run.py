# =========================================================================

# Script: scripts/cylc_run.py

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
    orchestrated by Cylc version 7.9.3; all Cylc versions <= 7.9.3 are
    supported, however Cylc versions >= 8.x.x is not supported.

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

    Henry R. Winterbottom; 04 January 2023

History
-------

    2023-01-04: Henry Winterbottom -- Initial implementation.

"""

# ----

import os
import time

from utils.arguments_interface import Arguments
from utils.logger_interface import Logger

from cylc.launcher import CylcLauncher

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

logger = Logger()

# ----


def main() -> None:
    """
    Description
    -----------

    This is the driver-level function to invoke the tasks within this
    script.

    """

    # Define the schema attributes.
    cls_schema = {"yaml_file": str}

    # Collect the command line arguments.
    script_name = os.path.basename(__file__)
    start_time = time.time()
    msg = f"Beginning application {script_name}."
    Logger().info(msg=msg)
    options_obj = Arguments().run(eval_schema=True, cls_schema=cls_schema)

    # Launch the task.
    cylc_launcher = CylcLauncher(yaml_file=options_obj.yaml_file)
    cylc_launcher.run()

    stop_time = time.time()
    msg = f"Completed application {script_name}."
    Logger().info(msg=msg)
    total_time = stop_time - start_time
    msg = f"Total Elapsed Time: {total_time} seconds."
    Logger().info(msg=msg)


# ----


if __name__ == "__main__":
    main()
