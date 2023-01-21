# =========================================================================

# Script: tools/cylc_workflow.py

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

""" """

# ----

import os
import time

from schema import Optional


from collections import OrderedDict

from confs.yaml_interface import YAML
from tools import parser_interface
from utils.arguments_interface import Arguments
from utils.error_interface import Error, msg_except_handle
from utils.logger_interface import Logger

from typing import Union

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcWorkflow:

    """ """

    def __init__(self, options_obj: object):
        """ """

        # Define the base-class attributes.
        self.logger = Logger()
        self.options_obj = options_obj

        # Initialize the graph types; the respective Python
        # dictionaries will be used to establish the respective
        # components of the Cylc workflow engine graph.
        (self.cold_start_dict, self.warm_start_dict, self.final_cycle_dict) = \
            [OrderedDict() for cycle_type in range(3)]

        # Parse the YAML-formatted experiment configuration file.
        self.yaml_dict = YAML().read_yaml(yaml_file=self.options_obj.yaml_file)

    def _family_check_(self, task_dict):
        """ """

        family = parser_interface.dict_key_value(
            dict_in=task_dict, key="family", force=True)
        if family is None:
            family = False

        return family

    def _get_currdepends(self, task_dict: dict) -> Union[dict, None]:
        """ """
        curr_cycle_dict = parser_interface.dict_key_value(
            dict_in=task_dict, key="currcycle_tasks", force=True, no_split=True)

        return curr_cycle_dict

    def _get_prevdepends(self, task_dict: dict) -> Union[dict, None]:
        """ """

        prev_cycle_dict = parser_interface.dict_key_value(
            dict_in=task_dict, key="prevcycle_tasks", force=True, no_split=True)

        return prev_cycle_dict

    def cold_start(self, task: str, task_dict: dict) -> None:
        """
        Description
        -----------

        This method builds Cylc the workflow engine graph strings for
        cold-start cycle tasks and updates the base-class attribute
        Python dictionary accordingly.

        Parameters
        ----------

        task: str

            A Python string specifying the Cylc workflow engine task.

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        """

        # Check whether the respective task is a cold-start cycle
        # task; proceed accordingly.
        cold_start = parser_interface.dict_key_value(
            task_dict, key="cold_start", force=True)

        if cold_start:

            # Collect only attributes for the current cycle and
            # proceed accordingly.
            curr_cycle_dict = self._get_currdepends(task_dict=task_dict)

            if curr_cycle_dict is not None:

                # Build the current cycle attributes for the
                # respective task.
                task_list = []
                for curr_task in curr_cycle_dict:

                    # Build the respective task upstream dependencies
                    # string; proceed accordingly.
                    task_str = f"{curr_task}:"
                    curr_task_dict = parser_interface.dict_key_value(
                        dict_in=curr_cycle_dict, key=curr_task, force=None,
                        no_split=True)

                    # Check whether the upstream task is a Cylc family
                    # task; proceed accordingly.
                    if self._family_check_(task_dict=curr_task_dict):
                        task_str = task_str + " succeed-all "

                    if not self._family_check_(task_dict=curr_task_dict):
                        task_str = task_str + " succeed "

                    # Append the updated string to the local Python
                    # list.
                    task_list.append(task_str)

                # Build the respective task dependency string and
                # update the base-class attribute.
                task_str = "& ".join(
                    [ctask for ctask in task_list]) + f"=> {task}"
                self.cold_start_dict[task] = task_str

        if not cold_start or None:
            pass

    def final_cycle(self, task_dict: dict) -> None:
        """ """

    def warm_start(self, task: str, task_dict: dict) -> None:
        """  """

        # Check whether the respective task is a warm-start cycle
        # task; proceed accordingly.
        warm_start = parser_interface.dict_key_value(
            task_dict, key="warm_start", force=True)

        if warm_start:

            # Collect only attributes for the previous cycle and
            # proceed accordingly.
            (task_list, task_str) = ([], str())
            prev_cycle_dict = self._get_prevdepends(task_dict=task_dict)

            if prev_cycle_dict is not None:

                # Build the previous cycle attributes for the
                # respective task.
                for prev_task in prev_cycle_dict:

                    # Build the respective task upstream dependencies
                    # string; proceed accordingly.
                    task_str = f"{prev_task}" + "[-{{ CYCLE_INTERVAL }}]:"
                    prev_task_dict = parser_interface.dict_key_value(
                        dict_in=prev_cycle_dict, key=prev_task, force=None,
                        no_split=True)

                    # Check whether the upstream task is a Cylc family
                    # task; proceed accordingly.
                    if self._family_check_(task_dict=prev_task_dict):
                        task_str = task_str + " succeed-all "

                    if not self._family_check_(task_dict=prev_task_dict):
                        task_str = task_str + " succeed "

                    # Append the updated string to the local Python
                    # list.
                    task_list.append(task_str)

            # Collect only attributes for the current cycle and
            # proceed accordingly.
            curr_cycle_dict = self._get_currdepends(task_dict=task_dict)

            if curr_cycle_dict is not None:

                # Build the current cycle attributes for the
                # respective task.
                for curr_task in curr_cycle_dict:

                    # Build the respective task upstream dependencies
                    # string; proceed accordingly.
                    task_str = f"{curr_task}:"
                    curr_task_dict = parser_interface.dict_key_value(
                        dict_in=curr_cycle_dict, key=curr_task, force=None,
                        no_split=True)

                    # Check whether the upstream task is a Cylc family
                    # task; proceed accordingly.
                    if self._family_check_(task_dict=curr_task_dict):
                        task_str = task_str + " succeed-all "

                    if not self._family_check_(task_dict=curr_task_dict):
                        task_str = task_str + " succeed "

                    # Append the updated string to the local Python
                    # list.
                    task_list.append(task_str)

            if len(task_list) > 0:
                self.warm_start_dict[task] = "& ".join(
                    [item for item in task_list]) + f"=> {task}"

        if not warm_start:
            pass

    def run(self) -> None:
        """ """

        # Loop through each task and proceed accordingly.
        for task in self.yaml_dict:

            # Collect the attributes for the respective task and
            # proceed accordingly.
            task_dict = parser_interface.dict_key_value(
                dict_in=self.yaml_dict, key=task, force=True)

            if task_dict is not None:

                # Collect the respective cycle type attributes (if
                # applicable).
                self.cold_start(task=task, task_dict=task_dict)
                self.warm_start(task=task, task_dict=task_dict)

                print(task, self.cold_start_dict[task])
                print(task, self.warm_start_dict[task])


class CylcWorkflowError(Error):
    """
    Description
    -----------

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    """


# ----


@msg_except_handle(CylcWorkflowError)
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



    """

    # Define the schema attributes.
    cls_schema = {"yaml_file": str, Optional("output_path"): str}

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
