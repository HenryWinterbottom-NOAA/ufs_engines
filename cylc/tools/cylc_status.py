# =========================================================================

# Script: tools/cylc_status.py

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

    cylc_status.py

Description
-----------

    This script is the driver script for all Cylc engine application
    task status; all Cylc versions <= 7.9.3 are supported, however
    Cylc versions >= 8.x.x is not supported.

Classes
-------

    CylcStatus(options_obj)

        This is the base-class object for all Cylc engine Cylc engine
        graph applications.

    CylcStatusError(msg)

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

Usage
-----

    user@host:$ python cylc_status.py --<database_path> --<output_path> --<to_output>

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

    Henry R. Winterbottom; 12 January 2023

History
-------

    2023-01-12: Henry Winterbottom -- Initial implementation.

"""

# ----

import json
import operator
import os
import sys
import time
from typing import Tuple

import colorama
import numpy
import tabulate
from ioapps import sqlite3_interface
from utils import timestamp_interface
from utils.arguments_interface import Arguments
from utils.error_interface import Error, msg_except_handle
from utils.logger_interface import Logger

from tools import datetime_interface, parser_interface

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcStatus:
    """
    Description
    -----------

    This is the base-class object for parsing a Cylc engine
    applicaiton database file and returning, both to the user terminal
    and an external file path, the attributes associated with the Cylc
    engine application tasks.

    Parameters
    ----------

    options_obj: object

        A Python object containing the command line argument
        attributes.

    """

    def __init__(self, options_obj: object):
        """
        Description
        -----------

        Creates a new CylcStatus object.

        """

        # Define the base-class attributes.
        self.logger = Logger()
        self.options_obj = options_obj
        self.cylc_table_list = ["task_jobs", "task_states"]

        # Define the output files; these will only be used if the
        # command line option to_output is True upon entry.
        self.stats_output_file = os.path.join(self.options_obj.output_path,
                                              "cylc-engine.stats")
        self.status_output_file = os.path.join(self.options_obj.output_path,
                                               "cylc-engine.status")

        # Format the boolean string provided upon entry.
        self.to_output = json.loads(self.options_obj.to_output.lower())

    def build_tables(self, database_obj: object) -> Tuple[list, list, list]:
        """
        Description
        -----------

        This method contructs and formats a table of the task
        attributes collected from the respective Cylc engine
        application workflow database tables.

        Parameters
        ----------

        database_obj: object

            A Python object containing the necessary/respective Cylc
            engine application workflow database tables.

        Returns
        -------

        table_list_file: list

            A Python list containing the table attributes to be
            written to the file path specified by the base-class
            attribute status_output_file.

        table_list_terminal: list

            A Python list containing the table attributes to be
            written to the user terminal; note that the status for the
            respective Cylc engine application workflow tasks are
            colorize as defined in the base-class method status_color.

        stats_list: list

            A Python list containing the Cylc engine application
            workflow task statistical diagnostics for the respective
            run-times.

        """

        # Initialize the respective tables to be returned and define
        # the respective attributes; proceed accordingly.
        (stats_list, table_list) = [[] for i in range(2)]

        for (_, task_attrs) in database_obj.task_jobs.items():

            # Define the relevant task attributes.
            (cycle, name, attempts, start, stop) = \
                (task_attrs[0], task_attrs[1], task_attrs[4], task_attrs[8],
                 task_attrs[9])

            # Define the current status for the task; proceed
            # accordingly.
            try:
                status = database_obj.task_states[f"{name}.{cycle}"][5]
                status = status.upper()

            except KeyError:
                status = None

            # Compute the total number of seconds for the respective
            # task; proceed accordingly.
            try:
                seconds = datetime_interface.elapsed_seconds(
                    start_datestr=start, stop_datestr=stop,
                    start_frmttyp=timestamp_interface.Y_m_dTHMSZ,
                    stop_frmttyp=timestamp_interface.Y_m_dTHMSZ)

            except TypeError:
                seconds = str()

            # Define the time attributes for the respective task;
            # proceed accordingly.
            cycle = datetime_interface.datestrupdate(
                datestr=cycle, in_frmttyp=timestamp_interface.YmdTHMZ,
                out_frmttyp=timestamp_interface.YmdTHMZ)

            try:
                start = datetime_interface.datestrupdate(
                    datestr=start, in_frmttyp=timestamp_interface.Y_m_dTHMSZ,
                    out_frmttyp=timestamp_interface.INFO)

            except TypeError:
                start = str()

            try:
                stop = datetime_interface.datestrupdate(
                    datestr=stop, in_frmttyp=timestamp_interface.Y_m_dTHMSZ,
                    out_frmttyp=timestamp_interface.INFO)

            except TypeError:
                stop = str()

            # Assemble the table row accordingly.
            if not self.to_output:
                status = self.status_color(status=status)
            row = [cycle, name, status, start, stop, seconds, attempts]
            table_list.append(row)

        table_list = sorted(table_list, key=operator.itemgetter(0))

        # Compute the timing statistics for the respective Cylc engine
        # application tasks; proceed accordingly.
        cylc_stats_dict = self.compute_stats(table=table_list)

        # Build the Cylc engine application tasks timing statistics
        # table.
        for (cylc_app, _) in cylc_stats_dict.items():
            cylc_stats = parser_interface.dict_key_value(
                dict_in=cylc_stats_dict, key=cylc_app)

            row = [cylc_stats[idx] for idx in range(4)]
            row.insert(0, cylc_app)
            stats_list.append(row)

        return (table_list, stats_list)

    def compute_stats(self, table: list) -> dict:
        """
        Description
        -----------

        This method computes the run-time statistics for the
        respective tasks collected from the Cylc engine application
        database.

        Parameters
        ----------

        table: list

            A Python list containing the Cylc engine application
            database attributes, formatted as a table.

        Returns
        -------

        cycl_stats_dict: dict

            A Python dictionary containing the run-time statistics for
            the respective Cylc engine application suite tasks.

        """

        # Gather the Cylc engine application task attributes; proceed
        # accordingly.
        (cylc_stats_dict, cylc_apps_list) = ({}, [])

        # Define a list of applications within the respective table.
        for item in table:
            cylc_apps_list.append(item[1])
        cylc_apps_list = sorted(list(set(cylc_apps_list)))

        # Compute the timing statistics for the respective Cylc engine
        # application tasks; proceed accordingly.
        for cylc_app in cylc_apps_list:
            (size, seconds_list) = (0, [])

            # Collect the attributes for the respective Cylc engine
            # application task.
            for item in table:
                if cylc_app in item:
                    seconds_list.append(item[5])
                    size = size + 1

            if size > 1:

                # Compute the statistical attributes for the
                # respective application
                seconds_list = numpy.array(
                    list(filter(None, seconds_list))).astype(float)
                mean = numpy.mean(seconds_list)
                median = numpy.median(seconds_list)
                vari = numpy.sqrt(numpy.var(seconds_list))

            else:

                # Define the respective statistical attributes for
                # single application tasks to NoneType.
                (mean, median, vari) = [None for i in range(3)]

            # Update the Cylc engine application task application
            # statistic attributes.
            cylc_stats_dict[cylc_app] = [mean, median, vari, size]

        return cylc_stats_dict

    def parse_database(self) -> object:
        """
        Description
        -----------

        This method parses the specified tables within the Cylc engine
        application SQLite3 database filepath, renames the dictionary
        keys in accordance with the Cylc engine application task and
        respective cycle, and defines the Python object attributes in
        accordance with the table name and the table dictionary.

        Returns
        -------

        database_obj: obj

            A Python object containing the contents of the respective
            database path tables.

        """

        # Collect the relevant tables from the Cylc engine application
        # database file path.
        database_obj = parser_interface.object_define()

        for cylc_table in self.cylc_table_list:

            # Define a Python dictionary containing the attributes for
            # the respective Cylc engine application database table.
            table_parse_dict = {}

            # Read the contents of the respective Cylc engine
            # application database table.
            cylc_table_dict = sqlite3_interface.read_table(
                path=self.options_obj.database_path, table_name=cylc_table)

            # Build the Python dictionary.
            for (element, _) in cylc_table_dict.items():
                name = cylc_table_dict[element][0]
                cycle = cylc_table_dict[element][1]

                table_parse_dict[f"{name}.{cycle}"] = cylc_table_dict[element]

            # Update the local Python object.
            database_obj = parser_interface.object_setattr(
                object_in=database_obj, key=cylc_table, value=table_parse_dict)

        return database_obj

    def status_color(self, status: str) -> str:
        """
        Description
        -----------

        This method assigns a color to the respective task status
        using the Python colorama library; if status is either
        NoneType or something other than succeeded, running, or failed
        upon entry, no color is assigned and the input string is
        simply returned.

        Parameters
        ----------

        status: str

            A Python string specifying the status of the Cylc engine
            application task.

        Returns
        -------

        status: str

            A Python string specifying the status of the Cylc engine
            application task but with the colorama attributes
            attached; if not one of the defined allowable status upon
            entry (or NoneType), the input status string is returned.

        """

        # Define the table cell color in accordance with status
        # attribute upon entry; proceed accordingly.
        reset = colorama.Back.RESET

        # Status of tasks which have succeeded.
        if status.lower() == 'succeeded':
            color = colorama.Back.CYAN

        # Status of tasks that are currently running.
        elif status.lower() == 'running':
            color = colorama.Back.GREEN

        # Status of tasks that have failed.
        elif status.lower() == 'failed':
            color = colorama.Back.RED

        # All other status returns.
        else:
            color = None

        # Assign the table cell color with respect to the task status.
        if color is not None:
            status = (color+status+reset)

        return status

    def write_table(self, table, run_stats: bool = False) -> None:
        """
        Description
        -----------

        This method writes the table provided upon entry using the
        tabulate library; if to_output is True upon entry, the
        respective table will also be written to the file path defined
        by the respective base-class attribute.

        Parameters
        ----------

        table: list

            A Python list containing the table to be written.

        Keywords
        --------

        runs_stats: bool, optional

            A Python boolean valued variable specifying whether the
            table to be written contains the run-time statistics for
            the respective Cylc suite tasks.

        """

        # Define the current timestamp.
        current_date = datetime_interface.current_date(
            frmttyp=timestamp_interface.INFO)
        current_date_str = (f"\n\nLast Updated: {current_date}\n")

        # Define the generic table attributes.
        table_kwargs = {'tablefmt': 'fancy_grid', 'numalign': 'center', 'stralign':
                        'center'}

        # Write the respective table accordingly.
        if run_stats:

            # Write the table containing the Cylc engine application
            # task run-time statistics.
            output_file = self.stats_output_file

            # Define the tabulate attributes.
            headers = ['Task', 'Mean Run Time (s)', 'Median Run Time (s)',
                       'Run Time Variability (s)', 'Total Number of Executions']
            disclaimer = ('\n\nCAUTION: Run-time statistics may not be accurate '
                          'representations of certain tasks depending upon the '
                          'user experiment configuration.')

        if not run_stats:

            # Write the table containing Cylc engine application task
            # status.
            output_file = self.status_output_file

            # Define the tabulate attributes.
            headers = ['Cycle', 'Task', 'Status', 'Start Time', 'Stop Time',
                       'Run Time (s)', 'Attempts']

        # Write the table.
        table_obj = tabulate.tabulate(table, headers, **table_kwargs)

        # Output the respective tables accordingly.
        sys.stdout.write(table_obj)
        if run_stats:
            sys.stdout.write(disclaimer)
        sys.stdout.write(current_date_str)

        # Write the respective table to the specified output file
        # path.
        if self.to_output:
            msg = (
                f"The output file containing Cylc task information is {output_file}.")
            self.logger.info(msg=msg)

            # Write the respective table to the specified output file;
            # proceed accordingly.
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(table_obj)
                if run_stats:
                    f.write("\n" + disclaimer)
                f.write(current_date_str)

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Parses the Cylc engine application database file
            containing the task attributes.

        (2) Builds files for both the respective Cylc engine
            application workflow tasks as well as statistical
            diagnostics for the respective tasks.

        (3) Writes the tables in accordance with the run-time
            parameters.

        """

        # Parse the Cylc engine application database and define the
        # attributes for the relevant tables.
        database_obj = self.parse_database()

        # Build the tabulated attributes using the attributes parsed
        # from the Cylc engine application database.
        (table_list, stats_list) = self.build_tables(database_obj=database_obj)

        # Write the respective tables accordingly.
        self.write_table(table=table_list, run_stats=False)
        self.write_table(table=stats_list, run_stats=True)


# ----


class CylcStatusError(Error):
    """
    Description
    -----------

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    """


# ----


@ msg_except_handle(CylcStatusError)
def __error__(msg: str) -> None:
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

    Parameters
    ----------

    database_path: str

        A Python string specifying the path to the Cylc engine
        application database.

    output_path: str

        A Python string specifying the path to which all output files
        will be written (if applicable).

    to_output: bool

        A Python boolean valued variable specifying whether to write
        the Cylc engine application task attributes to files beneath
        the output_path attribute.

    """

    # Define the schema attributes.
    cls_schema = {"database_path": str,
                  "output_path": str,
                  "to_output": bool}

    # Collect the command line arguments.
    script_name = os.path.basename(__file__)
    start_time = time.time()
    msg = f"Beginning application {script_name}."
    Logger().info(msg=msg)
    options_obj = Arguments().run(eval_schema=True, cls_schema=cls_schema)

    # Launch the task.
    task = CylcStatus(options_obj=options_obj)
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
