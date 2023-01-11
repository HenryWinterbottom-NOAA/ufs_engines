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


"""

# ----

import os
import tabulate
import time

from ioapps import sqlite3_interface
from tools import datetime_interface
from tools import parser_interface
from typing import Tuple
from utils import timestamp_interface
from utils.arguments_interface import Arguments
from utils.error_interface import Error, msg_except_handle
from utils.logger_interface import Logger


# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcStatus:
    """

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

    def build_tables(self, database_obj: object) -> Tuple[list, list]:
        """ """

        # Initialize the respective tables to be returned and define
        # the respective attributes; proceed accordingly.
        (table_list_file, table_list_terminal) = [[] for i in range(2)]

        for (task_job, task_attrs) in database_obj.task_jobs.items():

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
                    start_frmttyp=timestamp_interface.GENERAL,
                    stop_frmttyp=timestamp_interface.GENERAL)

            except TypeError:
                seconds = str()

    def parse_database(self) -> object:
        """

        """

        # Collect the relevant tables from the Cylc database file
        # path.
        database_obj = parser_interface.object_define()

        for cylc_table in self.cylc_table_list:

            # Define a Python dictionary containing the attributes for
            # the respective Cylc database table.
            table_parse_dict = {}

            # Read the contents of the respective Cylc database table.
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

    def run(self) -> None:
        """ """

        # Parse the Cylc database and define the attributes for the
        # relevant tables.
        database_obj = self.parse_database()

        # Build the tabulated attributes using the attributes parsed
        # from the Cylc database.
        self.build_tables(database_obj=database_obj)

# ----


class CylcStatusError(Error):
    """
    Description
    -----------

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    """


# ----


@msg_except_handle(CylcStatusError)
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

    """

    # Define the schema attributes.
    cls_schema = {"database_path": str}

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
