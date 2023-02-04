# =========================================================================

# Script: cylc/tools/cylc_workflow.py

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

    cylc_workflow.py

Description
-----------

    This script is the driver script for all Cylc engine workflow
    suite file generations and creations; all Cylc versions <= 7.9.3
    are supported, however Cylc versions >= 8.x.x is not supported.

Classes
-------

    CylcWorkflow(options_obj)

        This is the base-class object for all Cylc engine workflow
        Jinja2 formatted file generation and creations.

    CylcWorkflowError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Error.

Functions
---------

    main()

        This is the driver-level function to invoke the tasks within
        this script.

Usage
-----

    user@host:$ python cylc_workflow.py --<yaml_file> --<graph_template> --<output_path>

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications contained in
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Requirements
------------

- cylc-flow; https://github.com/cylc/cylc-flow (49a1683)

- ufs_pytils; https://github.com/HenryWinterbottom-NOAA/ufs_pyutils

Author(s)
---------

    Henry R. Winterbottom; 21 January 2023

History
-------

    2023-01-21: Henry Winterbottom -- Initial implementation.

"""

# ----

import os
import time

from utils.arguments_interface import Arguments
from utils.logger_interface import Logger

from cylc_tools.workflow import CylcWorkflow

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


def main() -> None:
    """
    Description
    -----------

    This is the driver-level function to invoke the tasks within this
    script.

    """

    # Define the schema attributes.
    cls_schema = {"yaml_file": str, "graph_template": str, "output_path": str}

    # Collect the command line arguments.
    script_name = os.path.basename(__file__)
    start_time = time.time()
    msg = f"Beginning application {script_name}."
    Logger().info(msg=msg)
    options_obj = Arguments().run(eval_schema=True, cls_schema=cls_schema)

    # Launch the task.
    task = CylcWorkflow(options_obj=options_obj)
    task.run()

    stop_time = time.time()
    msg = f"Completed application {script_name}."
    Logger().info(msg=msg)
    total_time = stop_time - start_time
    msg = f"Total Elapsed Time: {total_time} seconds."
    Logger().info(msg=msg)


# ----


if __name__ == "__main__":
    main()
