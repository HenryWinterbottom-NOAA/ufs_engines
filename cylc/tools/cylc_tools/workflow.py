# =========================================================================

# Module: cylc/tools/cylc_tools/workflow.py

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

    workflow.py

Description
-----------

    This module contains the base-class object for all Cylc engine
    workflow suite file generations.

Classes
-------

    CylcWorkflow(options_obj)

        This is the base-class object for all Cylc engine workflow
        suite file generations; it is a sub-class of CylcTools.

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

    Henry R. Winterbottom; 22 January 2023

History
-------

    2023-01-22: Henry Winterbottom -- Initial implementation.

"""

# ----

import os

from collections import OrderedDict
from typing import Union

from confs.yaml_interface import YAML
from tools import fileio_interface
from tools import parser_interface

from cylc_tools import CylcTools

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


class CylcWorkflow(CylcTools):
    """
    Description
    -----------

    This is the base-class object for all Cylc engine workflow suite
    file generations; it is a sub-class of CylcTools.

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

        Creates a new CylcWorkflow object.

        """

        # Define the base-class attributes.
        super().__init__(options_obj=options_obj)

        # Initialize the graph types; the respective Python
        # dictionaries will be used to establish the respective
        # components of the Cylc workflow engine graph.
        (self.cold_start_dict, self.warm_start_dict, self.final_cycle_dict) = [
            OrderedDict() for cycle_type in range(3)
        ]

        # Parse the YAML-formatted experiment configuration file.
        self.yaml_dict = YAML().read_yaml(yaml_file=self.options_obj.yaml_file)

    def _family_check_(self, task_dict):
        """
        Description
        -----------

        This method checks whether the specified cycle-type Python
        dictionary task contains the boolean attribute "family" and
        returns the value accordingly.

        Parameters
        ----------

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        Returns
        -------

        family: bool

            A Python boolean valued variable specifying whether the
            respective task is a Cylc engine "family" task.

        """

        # Parse the task dictionary and proceed accordingly.
        family = parser_interface.dict_key_value(
            dict_in=task_dict, key="family", force=True
        )
        if family is None:
            family = False

        return family

    def _get_currdepends(self, task_dict: dict) -> Union[dict, None]:
        """
        Description
        -----------

        This method collects the current-cycle dependecies for a
        specified Cylc engine task; if no current-cycle dependencies
        are specified within the experiment configuration, NoneType is
        returned.

        Parameters
        ----------

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        Returns
        -------

        curr_cycle_dict: dict or NoneType (see below)

            A Python dictionary containing the current-cycle
            dependencies; if no current-cycle dependencies are
            specified within the experiment configuration, NoneType is
            returned.

        """

        # Parse the task dictionary and proceed accordingly.
        curr_cycle_dict = parser_interface.dict_key_value(
            dict_in=task_dict, key="currcycle_tasks", force=True, no_split=True
        )

        return curr_cycle_dict

    def _get_prevdepends(self, task_dict: dict) -> Union[dict, None]:
        """
        Description
        -----------

        This method collects the previous-cycle dependecies for a
        specified Cylc engine task; if no previous-cycle dependencies
        are specified within the experiment configuration, NoneType is
        returned.

        Parameters
        ----------

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        Returns
        -------

        prev_cycle_dict: dict or NoneType (see below)

            A Python dictionary containing the previous-cycle
            dependencies; if no previous-cycle dependencies are
            specified within the experiment configuration, NoneType is
            returned.

        """

        prev_cycle_dict = parser_interface.dict_key_value(
            dict_in=task_dict, key="prevcycle_tasks", force=True, no_split=True
        )

        return prev_cycle_dict

    def cold_start(self, task: str, task_dict: dict) -> None:
        """
        Description
        -----------

        This method builds the Cylc workflow engine graph strings for
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
        msg = (
            f"Collecting cold-start cycle task {task} attributes from "
            f"experiment configuration file {self.options_obj.yaml_file}."
        )
        self.logger.info(msg=msg)

        cold_start = parser_interface.dict_key_value(
            task_dict, key="cold_start", force=True
        )

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
                        dict_in=curr_cycle_dict,
                        key=curr_task,
                        force=None,
                        no_split=True,
                    )

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
                task_str = "& ".join(set(task_list)) + f"=> {task}"
                self.cold_start_dict[task] = task_str

        if not cold_start:
            pass

    def final_cycle(self, task: str, task_dict: dict) -> None:
        """
        Description
        -----------

        This method builds the Cylc workflow engine graph strings for
        the final cycle tasks and updates the base-class attribute
        Python dictionary accordingly.

        Parameters
        ----------

        task: str

            A Python string specifying the Cylc workflow engine task.

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        """

        # Check whether the respective task is to run as a final cycle
        # task; proceed accordingly.
        msg = (
            f"Collecting final cycle task {task} attributes from experiment "
            f"configuration file {self.options_obj.yaml_file}."
        )
        self.logger.info(msg=msg)

        final_cycle = parser_interface.dict_key_value(
            task_dict, key="final_cycle", force=True
        )

        if final_cycle:

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
                        dict_in=prev_cycle_dict,
                        key=prev_task,
                        force=None,
                        no_split=True,
                    )

                    # Check whether the upstream task is a Cylc family
                    # task; proceed accordingly.
                    if self._family_check_(task_dict=prev_task_dict):
                        task_str = task_str + " succeed-all "

                    if not self._family_check_(task_dict=prev_task_dict):
                        task_str = task_str + " succeed "

                    # Append the updated string to the local Python
                    # list.
                    task_list.append(task_str)

                if len(task_list) > 0:
                    self.final_cycle_dict[task] = (
                        "& ".join(set(task_list)) + f"=> {task}"
                    )

        if not final_cycle:
            pass

    def warm_start(self, task: str, task_dict: dict) -> None:
        """
        Description
        -----------

        This method builds the Cylc workflow engine graph strings for
        warm-start cycle tasks and updates the base-class attribute
        Python dictionary accordingly.

        Parameters
        ----------

        task: str

            A Python string specifying the Cylc workflow engine task.

        task_dict: dict

            A Python dictionary containing the attributes for the
            respective task.

        """

        # Check whether the respective task is a warm-start cycle
        # task; proceed accordingly.
        msg = (
            f"Collecting warm-start cycle task {task} attributes from "
            f"experiment configuration file {self.options_obj.yaml_file}."
        )
        self.logger.info(msg=msg)

        warm_start = parser_interface.dict_key_value(
            task_dict, key="warm_start", force=True
        )

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
                        dict_in=prev_cycle_dict,
                        key=prev_task,
                        force=None,
                        no_split=True,
                    )

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
                        dict_in=curr_cycle_dict,
                        key=curr_task,
                        force=None,
                        no_split=True,
                    )

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
                    set(task_list)) + f"=> {task}"

        if not warm_start:
            pass

    def write_graph(self) -> None:
        """
        Description
        -----------

        This method writes the Cylc workflow engine task graph.

        """

        # Define the Python dictionaries to build the Cylc engine
        # workflow graph.
        yaml_dict = {}
        graph_dict = {
            "COLD_START_TASKS": self.cold_start_dict,
            "FINAL_CYCLE_TASKS": self.final_cycle_dict,
            "WARM_START_TASKS": self.warm_start_dict,
        }

        # Build the respective Cylc engine cycle types for the Cylc
        # engine workflow graph.
        for graph_type in graph_dict:

            # Collect the attributes for the respective graph type; if
            # NoneType the tasks for the respective graph type will
            # not be defined.
            tasks_dict = parser_interface.dict_key_value(
                dict_in=graph_dict, key=graph_type, force=True, no_split=True
            )

            # Build the respective graph type tasks; proceed
            # accordingly.
            if tasks_dict is not None:
                tasks_str = str()
                for task in tasks_dict:
                    value = parser_interface.dict_key_value(
                        dict_in=tasks_dict, key=task, no_split=True
                    )
                    tasks_str = tasks_str + value + "\n" + 3 * "\t"
                yaml_dict[graph_type] = tasks_str

        # Write the Cylc workflow engine graph.
        # msg = f"Writing Cylc workflow engine graph to file {yaml_path}."
        yaml_path = os.path.join(self.options_obj.output_path, "graph.rc")
        fileio_interface.dirpath_tree(path=os.path.dirname(yaml_path))
        YAML().write_tmpl(
            yaml_dict=yaml_dict,
            yaml_path=yaml_path,
            yaml_template=self.options_obj.graph_template,
        )

    def run(self) -> None:
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Collects the Cylc engine workflow attributes from the
            experiment configuration file and defines the attributes
            for the respective cold-start, warm-start, and final
            cycles.

        (2) Builds and writes the Cylc workflow engine graph.

        """

        # Loop through each task and proceed accordingly.
        for task in self.yaml_dict:

            # Collect the attributes for the respective task and
            # proceed accordingly.
            task_dict = parser_interface.dict_key_value(
                dict_in=self.yaml_dict, key=task, force=True
            )

            if task_dict is not None:

                # Collect the respective cycle type attributes (if
                # applicable).
                self.cold_start(task=task, task_dict=task_dict)
                self.warm_start(task=task, task_dict=task_dict)
                self.final_cycle(task=task, task_dict=task_dict)

        # Write the Cylc workflow engine graph.
        self.write_graph()
