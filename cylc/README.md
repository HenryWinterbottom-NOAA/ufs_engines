# UFS Engines Cylc Flow Applications

The Cylc engine version supported by this application is
[v7.9.3](https://github.com/cylc/cylc-flow/releases/tag/7.9.3). 

### Installing Cylc-flow

The Cylc-flow package may be collected and installed as follows for
non-supported machines.

~~~
user@host:$ git clone https://github.com/cylc/cylc.git /path/to/cylc
user@host:$ cd /path/to/cylc
user@host:$ git checkout tags/7.9.3
user@host:$ export PATH=/path/to/cylc/bin:$PATH
~~~

The Cylc engine has been installed for supportted RDHPCS platforms and
may be loaded for the respective platforms as follows.

### RDHPCS-Hera

~~~
user@host:$ module use -a /scratch2/BMC/gsienkf/UFS-RNR/UFS-RNR-stack/modules
user@host:$ module load cylc-flow
~~~

### RDHPCS-Orion

~~~
user@host:$ module use -a /work/noaa/gsienkf/UFS-RNR/UFS-RNR-stack/modules
user@host:$ module load cylc-flow
~~~

# Cylc Engine Workflow Tools

### Monitoring a Cylc Engine Workflow

To see the status for the respective active workflow suite tasks do as
follows.

~~~
user@host:$ cylc mon SPAM
~~~

where `SPAM` is the experiment name (`CYLCexptname`) provided in the
YAML-formatted [Cylc experiment configuration
file](./parm/cylc_demo.rdhpcs-hera.yaml).

The Cylc engine will inform the user as to whether the respective Cylc
workflow engine suite is registered and/or not running. If the Cylc
workflow engine suite is running, the active, pending, and recently
completed tasks will be listed in the terminal window.

### Pausing a Running Cylc Engine Workflow Suite

In order to pause an experiment, do the following:

~~~
user@host:$ cylc hold SPAM
~~~

Specific running Cylc engine suite tasks may also be put on hold as
follows.

~~~
user@host:$ cylc hold SPAM ham.20000101T0000Z
~~~

where `ham` is the name of an active Cylc engine workflow suite task
(or
[family](https://metomi.github.io/rose/2019.01.2/html/tutorial/cylc/runtime/configuration-consolidation/families.html))
and `20000101T0000Z` is the respective cycle timestamp, formatted as
`%Y%m%dT%H%MZ` assuming the POSIX convention.. Wildcard characters are
also permitted for activer Cylc engine workflow suite application
tasks. Finally, to release or run jobs that had been put on hold, do
the following.

~~~
`user@host:$ cylc release SPAM`
~~~

### Stopping an Active Cylc Engine Workflow Suite

An active Cylc engine workflow suite may be shut down as follows.

~~~
user@host:$ cylc stop SPAM
~~~

This will allow only currently launched tasks (including those in
queue) to complete. To immediately stop the entirety of the active
Cylc engine workflow suite, including those both running and queued,
do as follows.

~~~
user@host:$ cylc stop --now --now SPAM
~~~

### Addressing Failed Cylc Engine Workflow Suite Tasks

If configured accordingly, the Cylc engine workflow suite may inform
the user of failed tasks via email. Also the following command will
allow the user to see failed tasks.

~~~
user@host:$ cylc mon SPAM
~~~

To investigate why a specific task failed, the user may view the
run-time log as follows.

~~~
user@host:$ cylc log -f <logger_flag> SPAM ham.20000101T0000Z
~~~

Here `-f` denotes the type of logger output. The available logger
types/outputs and their usage for the example experiment `SPAM` are
listed in the following table.

<div align="center">

| Cylc Logger Command | Cylc Task File | Usage |
| :-------------: | :-----------: | :-----------: |
| a | `job-activity.log` | `user@host:$ cylc log -f a SPAM ham.20000101T0000Z` | 
| d | `job-edit.diff` | `user@host:$ cylc log -f d SPAM ham.20000101T0000Z` |
| e | `job.err` | `user@host:$ cylc log -f e SPAM ham.20000101T0000Z` |
| j | `job` | `user@host:$ cylc log -f d SPAM ham.20000101T0000Z` | 
| o | `job.out` | `user@host:$ cylc log -f o SPAM ham.20000101T0000Z` |
| s | `job.status` | `user@host:$ cylc log -f s SPAM ham.20000101T0000Z` | 
| x | `job.xtrace` | `user@host:$ cylc log -f x SPAM ham.20000101T0000Z` |
 
</div>

Alternatively, the user may also inspect the respective log files for
a Cylc engine workflow cycle task beneath
`cylc/SPAM/log/job/20000101T0000Z/ham/NN` for an existing Cylc engine
workflow suite.

### Restarting Failed Cylc Engine Workflow Suite Tasks

A failed task may be re-attempted by triggering the respective task as
follows.

~~~
user@host:$ cylc trigger SPAM ham.20000101T0000Z
~~~

To manipulate the status of a given task, the following may be used.

~~~
user@host:$ cylc reset --state=succeeded SPAM ham.20000101T0000Z
~~~

In the above example, the user is informing the Cylc workflow manager
that the `ham` task has completed successfully (i.e.,
`succeeded`). The available Cylc task states can be found
[here](https://cylc.github.io/cylc-doc/stable/html/running-suites.html#task-states-explained)

As an alternative to the above, a utility script is provided to not
only reset the state for a failed (parent) task, but also the
downstream (e.g., dependent) tasks that require the success of the
parent task. The script may be executed as follows using RDHPCS-Hera
as an example.

~~~
user@host:$ module use -a /scratch2/BMC/gsienkf/UFS-RNR/UFS-RNR-stack/modules
user@host:$ module load anaconda3
user@host:$ module load cylc-flow
user@host:$ python /path/to/cylc/cylc_reset.py --yaml_file=/path/to/ufs_engines/cylc/parm/cylc_demo.rdhpcs-hera.yaml --status=succeeded --task=ham --cycle=20010101000000 [--depends=/path/toufs_engines/demo/cylc/depends.yaml]
~~~

In the above example the `task_name` attribute may be any task within
the respective Cylc engine workflow suite. The `state` may be any
value listed
[here](https://cylc.github.io/cylc-doc/stable/html/running-suites.html#task-states-explained). The
Note that the Cylc engine workflow cycle is formatted as
`%Y%m%d%H%M%S` assuming the POSIX convention. Finally, the `depends`
attribute is an optional string specifying the path to a
YAML-formatted file containing the Cylc engine workflow suite parent
and respective child (e.g., downstream) tasks. And example can be
found [here](../../demo/cylc/depends.yaml).

### Restarting a Stopped Cylc Suite

It is often useful to shutdown a Cylc suite for various reasons, most
notably during platform maintenance periods. In order to restart the
respective Cylc workflow suite, the following command may be used.

~~~
user@host:$ cylc restart SPAM
~~~

# Resetting Active Cylc Engine Workflow Tasks Failing to Submit

Infrequently a Cylc engine workflow task attempts to submit but fails.
In the he following example we assume that a task `ham` fails to
submit for cycle `20000101T0000Z`.

~~~
user@host:$ cylc restart SPAM
user@host:$ cylc trigger SPAM ham.20000101T0000Z
~~~

In the above example, the Cylc engine workflow suite `SPAM` is
restarted. Next, the task `ham` for workflow cycle `20000101T0000Z` is
triggered such that it will be submitted again.

#

Please direct questions to [Henry
R. Winterbottom](mailto:henry.winterbottom@noaa.gov?subject=[UFS-Engines)