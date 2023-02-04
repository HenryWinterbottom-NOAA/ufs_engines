# =========================================================================

# Module: tools/rocoto_tools/__init__.py

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

    This module loads the rocoto_tools package.

Classes
-------

    RocotoTools(options_obj)

        This is the base-class object for all Rocoto tools sub-classes.

    RocotoToolsError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Error.

Functions
---------

    error(msg)

        This function is the exception handler for the respective
        module.

Requirements
------------

- rocoto; https://github.com/christopherwharrop/rocoto

- ufs_pytils; https://github.com/HenryWinterbottom-NOAA/ufs_pyutils

Author(s)
---------

    Henry R. Winterbottom; 04 February 2023

History
-------

    2023-02-04: Henry Winterbottom - - Initial implementation.

"""

# ----

# pylint: disable=unused-argument

# ----

from dataclasses import dataclass

from utils.error_interface import Error, msg_except_handle
from utils.logger_interface import Logger

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----


@dataclass
class RocotoTools:
    """
    Description
    -----------

    This is the base-class object for all Rocoto tools sub-classes.

    Parameters
    ----------

    options_obj: object

        A Python object containing the command line argument
        attributes.

    """

    def __init__(self, options_obj: object):
        """
        Description
        ------------

        Creates a new RocotoTools object.

        """

        # Define the base-class attributes.
        self.logger = Logger()
        self.options_obj = options_obj


# ----


class RocotoToolsError(Error):
    """
    Description
    -----------

        This is the base-class for all exceptions; it is a sub-class
        of Error.

    """


# ----


@msg_except_handle(RocotoToolsError)
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
