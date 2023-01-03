# =========================================================================

# $$$ MODULE DOCUMENTATION BLOCK

# UFS-RNR-cylc :: ush/cylcutils/cylc_interface.py

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

    cylc_interface.py

Description
-----------

    This module contains the Cylc version 7.9.x workflow orchestrator
    interfaces.

Classes
-------

    CylcApplication(yaml_obj):

        This is the base-class object for all Cylc workflow
        orchestrator applications.

    CylcError(msg)

        This is the base-class for all exceptions; it is a sub-class
        of Exceptions.

    CylcLauncher(yaml_obj, suite_path)

        This is the base-class object which registers and launches a
        specified Cylc suite for the respective experiment; it is a
        sub-class of CylcApplication.

    CylcResetTasks(yaml_obj, expt_obj)

        This is the base-class object which resets the state of
        specified Cylc workflow tasks for the respective experiment;
        it is a sub-class of CylcApplication.

Note(s)
-------

    This module does not support Cylc 8.0.x; please download and
    install the Cylc applications contained in
    https://github.com/cylc/cylc-flow/archive/refs/tags/7.9.3.tar.gz.

Author(s)
---------

    Henry R. Winterbottom; 01 October 2022

History
-------

    2022-10-01: Henry Winterbottom -- Initial implementation.

"""

# ----

__author__ = "Henry R. Winterbottom"
__maintainer__ = "Henry R. Winterbottom"
__email__ = "henry.winterbottom@noaa.gov"

# ----

import os
import subprocess
import sys

from produtil.error_interface import Error
from produtil.logger_interface import Logger

# ----


class CylcApplication(object):
    """
    Description
    -----------

    This is the base-class object for all Cylc workflow orchestrator
    applications.

    Parameters
    ----------

    yaml_obj: obj

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.

    """

    def __init__(self, yaml_obj):
        """
        Description
        -----------

        Creates new CylcApplication object.

        """

        # Define the base-class attributes.
        self.yaml_obj = yaml_obj
        self.logger = Logger()
        self.run_dir = os.path.join(self.yaml_obj.WORKrnr,
                                    self.yaml_obj.experiment_name, 'cylc')
        self.get_cylc_app()

    def close_loggers(self, stderr, stdout):
        """
        Description
        -----------

        This method closes the open file logger objects.

        Parameters
        ----------

        stderr: obj

            A Python object specifying the standard error logger
            attributes.

        stdout: obj

            A Python object specifying the standard output logger
            attributes.

        """

        # Close the respective open file logger objects; proceed
        # accordingly.
        try:
            stderr.close()
        except Exception:
            pass

        try:
            stdout.close()
        except Exception:
            pass

    def get_cylc_app(self):
        """
        Description
        -----------

        This method checks whether the Cylc application executable is
        loaded within the user run-time environment; if so, the
        base-class attribute cylc_app is defined; if not, a CylcError
        exception is thrown.

        Raises
        ------

        CylcError:

            * raised if the cylc application executable path can not
              be determined from the run-time environment.

        """

        # Parse the run-time environment for the Cylc executable;
        # proceed accordingly.
        cmd = ['which', 'cylc']
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        if len(out) > 0:
            self.cylc_app = out.rstrip().decode('utf-8')
        else:
            msg = ('The cylc executable could not be determined for your system; '
                   'please check that the appropriate Cylc module is loaded. '
                   'Aborting!!!')
            raise CylcError(msg=msg)
        msg = ('The Cylc application path is {0}.'.format(self.cylc_app))
        self.logger.info(msg=msg)

    def open_loggers(self, errlog=None, outlog=None):
        """
        Description
        -----------

        This method defines and/or opens the file logger objects for
        the standard error and standard output streams.

        Keywords
        --------

        errlog: str, optional

            A Python string specifying the path to the standard error
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        outlog: str, optional

            A Python string specifying the path to the standard output
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        Returns
        -------

        stderr: obj

            A Python object specifying the standard error logger
            attributes.

        stdout: obj

            A Python object specifying the standard output logger
            attributes.        

        """

        # Define the file paths for the standard output and standard
        # error; proceed accordingly.
        if errlog is None:
            stderr = subprocess.PIPE
        if errlog is not None:
            stderr = open(errlog, 'w')

        if outlog is None:
            stdout = subprocess.PIPE
        if outlog is not None:
            stdout = open(outlog, 'w')

        return (stderr, stdout)

    def run_task(self, cmd, errlog=None, outlog=None):
        """
        Description
        -----------

        This method launches the command(s) specified in the commands
        list upon entry.

        Parameters
        ----------

        cmd: list

            A Python list containing the command(s) to be launched.

        Keywords
        --------

        errlog: str, optional

            A Python string specifying the path to the standard error
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        outlog: str, optional

            A Python string specifying the path to the standard output
            file path; if Nonetype upon entry, the logger object
            assumes subprocess.PIPE.

        Return
        ------

        returncode: int

            A Python integer specifying the return code provided by
            the subprocess command.

        """

        # Open the standard error and standard output file paths.
        (stderr, stdout) = self.open_loggers(
            errlog=errlog, outlog=outlog)

        # Launch the command(s) specified in the commands list.
        proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
        proc.wait()
        proc.communicate()
        returncode = proc.returncode

        # Close the file paths for the standard output and standard
        # error.
        self.close_loggers(stderr=stderr, stdout=stdout)

        return returncode

# ----


class CylcError(Error):
    """
    Description
    -----------

    This is the base-class for all exceptions; it is a sub-class of
    Exceptions.

    Parameters
    ----------

    msg: str, optional

        A Python string to accompany the raised exception.

    """

    def __init__(self, msg):
        """
        Description
        -----------

        Creates a new CylcError object.

        """
        super(CylcError, self).__init__(msg=msg)

# ----


class CylcLauncher(CylcApplication):
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

    def __init__(self, yaml_obj, suite_path):
        """
        Description
        -----------

        Creates a new CylcLauncher object.

        """

        # Define the base-class attributes.
        super(CylcLauncher, self).__init__(yaml_obj=yaml_obj)
        self.suite_path = suite_path

    def register_suite(self):
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
        errlog = os.path.join(self.run_dir, 'cylc_register.err')
        outlog = os.path.join(self.run_dir, 'cylc_register.out')

        # Define the subprocess command string.
        cmd = [self.cylc_app,
               'register',
               self.yaml_obj.experiment_name,
               self.suite_path,
               '--run-dir',
               self.run_dir]

        # Register the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = ('Cylc workflow suite {0} registered to {1}.'.
                   format(self.suite_path, self.yaml_obj.experiment_name))
            self.logger.info(msg=msg)
        if returncode != 0:
            msg = ('Registering Cylc workflow suite {0} failed! Please refer to '
                   '{1} for more information. Aborting!!!'
                   .format(self.suite_path, errlog))
            raise CylcError(msg=msg)

    def run_suite(self):
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
        errlog = os.path.join(self.run_dir, 'cylc_run.err')
        outlog = os.path.join(self.run_dir, 'cylc_run.out')

        # Define the subprocess command string.
        cmd = [self.cylc_app,
               'run',
               self.yaml_obj.experiment_name]

        # Run the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = ('Cylc workflow suite {0} launched as {1}.'
                   .format(self.suite_path, self.yaml_obj.experiment_name))
            self.logger.info(msg=msg)
        if returncode != 0:
            msg = ('Launching Cylc workflow suite {0} failed! Please refer to '
                   '{1} for more information.'.format(self.suite_path, errlog))
            raise CylcError(msg=msg)

    def run(self):
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Registers the specified Cylc suite for the respective
            experiment.

        (2) Launches(e.g., runs) the specified Cylc suite for the
            respective experiment.

        """

        # Register the Cylc experiment suite.
        self.register_suite()

        # Launch the Cylc experiment suite.
        self.run_suite()

# ----


class CylcResetTasks(CylcApplication):
    """
    Description
    -----------

    This is the base-class object which resets the state of specified
    Cylc workflow tasks for the respective experiment; it is a
    sub-class of CylcApplication.

    Parameters
    ----------

    yaml_obj: obj 

        A Python object containing the user options collected from
        experiment YAML-formatted configuration file.

    expt_obj: obj

        A Python object containing the experiment attributes required
        to reset the respective experiment Cylc workflow tasks; this
        includes the user-specified state to which to reset and the
        respective tasks for which the state is to be reset.

    """

    def __init__(self, yaml_obj, expt_obj):
        """
        Description
        -----------

        Creates a new CylcResetTasks object.

        """

        # Define the base-class attributes.
        super(CylcResetTasks, self).__init__(yaml_obj=yaml_obj)
        self.get_cylc_app()
        self.expt_obj = expt_obj

    def reset_suite(self):
        """
        Description
        -----------

        This method resets the tasks within the specified Cylc suite
        for the respective experiment.

        """

        # Define the file paths for the standard output and standard
        # error.
        errlog = os.path.join(self.run_dir, 'cylc_reset.{0}.err'
                              .format(self.expt_obj.cycle))
        outlog = os.path.join(self.run_dir, 'cylc_reset.{0}.out'
                              .format(self.expt_obj.cycle))

        # Define the subprocess command string.
        cmd = [self.cylc_app,
               'reset',
               '--state={0}'.format(self.expt_obj.status),
               self.yaml_obj.experiment_name
               ]
        for task in self.expt_obj.tasks:
            cmd.append(task)

        # Run the Cylc application suite; proceed accordingly.
        returncode = self.run_task(cmd=cmd, errlog=errlog, outlog=outlog)
        if returncode == 0:
            msg = ('The resetting of experiment {0} task(s) {1} was successful.'
                   .format(self.yaml_obj.experiment_name,
                           ', '.join(self.expt_obj.tasks)))
            self.logger.info(msg=msg)

    def run(self):
        """
        Description
        -----------

        This method performs the following tasks:

        (1) Resets the tasks within the specified Cylc suite for the
            respective experiment.

        """

        # Reset the specified Cylc experiment tasks.
        self.reset_suite()
