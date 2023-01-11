# =========================================================================

# Script: tools/cylc_graph.py

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

    cylc_graph.py

Description
-----------

    This script is the driver script for all Cylc engine workflow
    suite graph images; all Cylc versions <= 7.9.3 are supported,
    however Cylc versions >= 8.x.x is not supported.

Classes
-------

    CylcGraph(options_obj)

        This is the base-class object for all Cylc engine Cylc engine
        graph applications.

    CylcGraphError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Error.

Functions
---------

    __error__(msg)

        This function is the exception handler for the respective
        module.

    main()

        This is the driver-level function to invoke the tasks within
        this script.

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

    Henry R. Winterbottom; 11 January 2023

History
-------

    2023-01-11: Henry Winterbottom -- Initial implementation.

"""

# ----

# pylint: disable=broad-except
# pylint: disable=unused-argument

# ----

import os
import re
import time

from execute import subprocess_interface
from utils import timestamp_interface
from utils.arguments_interface import Arguments
from utils.error_interface import Error, msg_except_handle
from utils.logger_interface import Logger

from tools import datetime_interface, parser_interface, system_interface

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcGraph:
    """
    Description
    -----------

    This is the base-class object for all Cylc engine Cylc engine
    graph applications.

    """

    def __init__(self, options_obj: object):
        """
        Description
        -----------

        Creates a new CylcGraph object.

        """

        # Define the base-class attributes.
        self.logger = Logger()
        self.options_obj = options_obj
        self.cylc_app = system_interface.get_app_path(app="cylc")
        self.suite_path = options_obj.suite_path
        self.output_path = options_obj.output_path

    def collect_exptattrs(self) -> object:
        """
        Description
        -----------

        This method collects the Cylc engine application experiment
        suite attributes required to create each Cylc engine graph.

        Returns
        -------

        exptattrs_obj: object

            A Python object containing the respective Cyle engine
            application experiment suite (i.e., experiment.rc)
            attributes.

        Raises
        ------

        CylcGraphError:

            * raised if a mandatory attribute required to generate a
              Cylc engine graph image cannot be determined from the
              Cylc engine experiment configuration suite (i.e.,
              experiment.rc).

        """

        # Read the contents of the experiment attributes suite file.
        with open(
            os.path.join(self.suite_path, "experiment.rc"), "r", encoding="utf-8"
        ) as file:
            attrs_list = file.read().split("\n")

        # Define the respective attributes to construct the Cylc
        # engine workflow application graph.
        mand_attrs_list = [
            "CYLCexptname",
            "CYCLE_INTERVAL",
            "FINAL_CYCLE_POINT",
            "INITIAL_CYCLE_POINT",
        ]

        # Collect the respective attributes to construct the Cylc
        # engine workflow application graph; proceed accordingly.
        exptattrs_obj = parser_interface.object_define()

        for mand_attr in mand_attrs_list:
            for attr in attrs_list:

                # If the respective mandatory attribute has been
                # determined, proceed accordingly.
                if mand_attr in attr:
                    value = attr.split()[4]

                    if mand_attr.lower() == "cycle_interval":
                        value = int(re.sub("[PTS'\"]", "", value))
                    else:
                        value = re.sub("['\"]", "", value)
                    exptattrs_obj = parser_interface.object_setattr(
                        object_in=exptattrs_obj, key=mand_attr, value=value
                    )

            if mand_attr not in vars(exptattrs_obj):
                msg = (
                    f"The mandatory attribute {mand_attr} could not be "
                    f"determined from file {self.options_obj.exptattrs}. "
                    "Aborting!!!"
                )
                __error__(msg=msg)

        return exptattrs_obj

    def cylc_graph(self, exptattrs_obj: object) -> None:
        """
        Description
        -----------

        This method creates a Portable Network Graphic (PNG) images
        for the initial (i.e., cold-started), cycling (i.e.,
        warm-started), and final (i.e., last warm-started)
        applications for a specified Cylc engine workflow suite.

        Parameters
        ----------

        exptattrs_obj: object

            A Python object containing the respective Cyle engine
            application experiment suite (i.e., experiment.rc)
            attributes.

        Raises
        ------

        CylcGraphError:

            * raised if an exception is encountered while attempting
              to create a Cylc engine graph type.

        """

        # Define a Python dictionary containing the attributes for all
        # Cylc graphs to be created; the Python dictionary keys are
        # the respective graph types to be created.
        cylc_graph_dict = {
            # Cycling (i.e., warm-started) applications.
            "cycling": {
                "initial_cycle_point": exptattrs_obj.INITIAL_CYCLE_POINT,
                "final_cycle_point": datetime_interface.datestrupdate(
                    datestr=exptattrs_obj.INITIAL_CYCLE_POINT,
                    in_frmttyp=timestamp_interface.YmdTHMS,
                    out_frmttyp=timestamp_interface.YmdTHMS,
                    offset_seconds=exptattrs_obj.CYCLE_INTERVAL,
                ),
                "output_file": os.path.join(
                    self.output_path, f"{exptattrs_obj.CYLCexptname}.graph.cycling.png"
                ),
            },
            # Initial (i.e., cold-started) applications.
            "initial": {
                "initial_cycle_point": exptattrs_obj.INITIAL_CYCLE_POINT,
                "final_cycle_point": exptattrs_obj.INITIAL_CYCLE_POINT,
                "output_file": os.path.join(
                    self.output_path, f"{exptattrs_obj.CYLCexptname}.graph.initial.png"
                ),
            },
            # Final (i.e., last warm-started) applications.
            "final": {
                "initial_cycle_point": exptattrs_obj.FINAL_CYCLE_POINT,
                "final_cycle_point": exptattrs_obj.FINAL_CYCLE_POINT,
                "output_file": os.path.join(
                    self.output_path, f"{exptattrs_obj.CYLCexptname}.graph.final.png"
                ),
            },
        }

        # Build the Cylc graph image for each specified graph
        # type/time; proceed accordingly.
        for (cylc_graph, _) in cylc_graph_dict.items():

            try:

                msg = f"Creating graph images for workflow type {cylc_graph}."
                self.logger.info(msg=msg)

                # Define the arguments for the respective Cylc engine
                # graph image type.
                dict_in = parser_interface.dict_key_value(
                    dict_in=cylc_graph_dict, key=cylc_graph, no_split=True
                )

                output_file_path = parser_interface.dict_key_value(
                    dict_in=cylc_graph_dict[cylc_graph],
                    key="output_file",
                    no_split=True,
                )

                msg = f"Output image path for workflow type {cylc_graph} is {output_file_path}."
                self.logger.info(msg=msg)

                # Create the respective Cylc engine graph image type.
                cmd = [
                    "graph",
                    os.path.join(self.suite_path, "suite.rc"),
                    parser_interface.dict_key_value(
                        dict_in=dict_in, key="initial_cycle_point", no_split=True
                    ),
                    parser_interface.dict_key_value(
                        dict_in=dict_in, key="final_cycle_point", no_split=True
                    ),
                    "--output-file",
                    output_file_path,
                ]

                subprocess_interface.run(
                    exe=self.cylc_app,
                    job_type="app",
                    args=cmd,
                    errlog=os.path.join(
                        os.getcwd(),
                        f"err.{exptattrs_obj.CYLCexptname}.graph.{cylc_graph}.log",
                    ),
                    outlog=os.path.join(
                        os.getcwd(),
                        f"out.{exptattrs_obj.CYLCexptname}.graph.{cylc_graph}.log",
                    ),
                )
            except Exception as error:
                msg = (
                    f"Cylc graph application for type {cylc_graph} failed with error ",
                    f"{error}. Aborting!!!",
                )
                __error__(msg=msg)

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Collects the Cylc engine application experiment attributes
            for the correspoding Cylc engine workflow application
            experiment.rc suite.

        (2) Builds/creates the Cylc engine graph images for the
            corresponding Cylc engine graph types.

        """

        # Collect the Cylc engine application experiment attributes.
        exptattrs_obj = self.collect_exptattrs()

        # Build/create the Cylc engine graph images.
        self.cylc_graph(exptattrs_obj=exptattrs_obj)


# ----


class CylcGraphError(Error):
    """
    Description
    -----------

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    """


# ----


@msg_except_handle(CylcGraphError)
def __error__(msg: str = None) -> None:
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

    This is the driver-level function to invoke the tasks within this
    script.

    """

    # Define the schema attributes.
    cls_schema = {"suite_path": str, "output_path": str}

    # Collect the command line arguments.
    script_name = os.path.basename(__file__)
    start_time = time.time()
    msg = f"Beginning application {script_name}."
    Logger().info(msg=msg)
    options_obj = Arguments().run(eval_schema=True, cls_schema=cls_schema)

    # Launch the task.
    task = CylcGraph(options_obj=options_obj)
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
