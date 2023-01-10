# UFS Engines Cylc Flow Applications

The Cylc engine version supported by this application is
[v7.9.3](https://github.com/cylc/cylc-flow/releases/tag/7.9.3). The
Cylc engine is installed for supportted RDHPCS platforms and may be
loaded for the respective (supported) platforms as follows.

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

### Installing Cylc-flow

The Cylc-flow package may be collected and installed as follows for
non-supported machines.

~~~
user@host:$ git clone https://github.com/cylc/cylc.git /path/to/cylc
user@host:$ cd /path/to/cylc
user@host:$ git checkout tags/7.9.3
user@host:$ export PATH=/path/to/cylc/bin:$PATH
~~~

# Cylc Engine Workflow Tools

### Monitoring a Cylc Engine Workflow

To see the status of the respective tasks for a Cylc engine
application (experiment; i.e., `CYLCexptname`) do as follows.

~~~
user@host:$ cylc mon <experiment_name>
~~~

where `<experiment_name>` is the experiment name provided in the
YAML-formatted [Cylc experiment configuration
file](./parm/cylc_demo.rdhpcs-hera.yaml).

Cylc will inform the user as to whether the respective Cylc workflow
engine suite is registered and/or not running. If the Cylc workflow
engine suite is running, the active, pending, and recently completed
tasks will be listed in the terminal window.

### Pausing a Running Cylc Engine Workflow Suite

In order to pause an experiment, do the following:

~~~
user@host:$ cylc hold <experiment_name>
~~~

Specific running Cylc engine suite tasks may also be put on hold as
follows.

~~~
user@host:$ cylc hold <experiment_name> <task_name>.<DTG>
~~~

where `task_name` is the respective Cylc task (or
[family](https://metomi.github.io/rose/2019.01.2/html/tutorial/cylc/runtime/configuration-consolidation/families.html))
and `DTG` is the respective cycle timestamp, formatted as (assuming
the POSIX convention) `%Y%m%dT%H%MZ`. Wildcard characters are also
permitted for Cylc workflow application tasks. Finally, to
release or run jobs that had been put on hold, do as follows.

~~~
`user@host:$ cylc release <experiment_name>`
~~~

### Stopping a Running Cylc Engine Workflow Suite

An active Cylc engine workflow suite may be shut down as follows.

~~~
user@host:$ cylc stop <experiment_name>
~~~

This will allow only currently launched tasks (including those in
queue) to complete. To immediately stop the entirety of the Cylc
engine workflow suite, including those in the queue, do as follows.

~~~
user@host:$ cylc stop --now --now <experiment_name>
~~~

### Addressing Failed Cylc Engine Workflow Tasks

If configured accordingly, the Cylc engine workflow suite may inform
the user of failed tasks via email. Also the following command will
allow the user to see failed tasks.

~~~
user@host:$ cylc mon <experiment_name>
~~~

To investigate why a specific task failed, the user may view the
run-time log as follows.

~~~
user@host:$ cylc log -f <logger_flag> <experiment_name> <task_name>.<DTG>
~~~

Here `-f` denotes the type of logger output. The available logger
types/outputs are listed in the following table.

<div align="center">

| Cylc Logger Command | Cylc Task File | Usage |
| :-------------: | :-----------: | :-----------: |
| a | `job-activity.log` | `user@host:$ cylc log -f a <experiment_name> <task_name>.<DTG>` | 
| d | `job-edit.diff` | `user@host:$ cylc log -f d <experiment_name> <task_name>.<DTG>` |
| e | `job.err` | `user@host:$ cylc log -f e <experiment_name> <task_name>.<DTG>` |
| j | `job` | `user@host:$ cylc log -f d <experiment_name> <task_name>.<DTG>` | 
| o | `job.out` | `user@host:$ cylc log -f o <experiment_name> <task_name>.<DTG>` |
| s | `job.status` | `user@host:$ cylc log -f s <experiment_name> <task_name>.<DTG>` | 
| x | `job.xtrace` | `user@host:$ cylc log -f x <experiment_name> <task_name>.<DTG>` |
 
</div>

In the above example, the `e` allows the user to evaluate the
`job.err` file for the respective cycle task.

Alternatively, the user may also inspect the respective log files
directly beneath `cylc/<experiment_name>/log/job/<DTG>/<task_name>/NN`
for the respective UFS-RNR experiment.

### Restarting Failed UFS-RNR Cylc Tasks

A failed task may be restarted by triggering the respective task as follows:

`user@host:$ cylc trigger <experiment_name> <task_name>.<DTG>`

In order to manipulate the status of a given task, the user can do the
following:

`user@host:$ cylc reset --state=succeeded <experiment_name> <task_name>.<DTG>`

In the above example, the user is informing the Cylc workflow manager
that the given tasks has completed successfully (i.e.,
`succeeded`). The available Cylc task states can be found
[here](https://cylc.github.io/cylc-doc/stable/html/running-suites.html#task-states-explained)

As an alternative to the above, a utility script is provided to not
only reset the state for a failed (parent) task, but all of the
downstream dependent tasks that require the success of the parent
task. The script may be executed as follows.

### RDHPCS Hera

~~~
user@host:$ module use -a /scratch2/BMC/gsienkf/UFS-RNR/UFS-RNR-stack/modules
user@host:$ module load anaconda3
user@host:$ module load cylc-flow
user@host:$ python cylc_reset_ufsrnr.py --yaml /path/to/ufsrnr/cylc/experiment/yamlfile --status <state> --task <task_name> --cycle <cycle> [--depends </path/to/ufsrnr/runtime/depends/yamlfile>]
~~~

In the above example the `task_name` attribute may be any task listed
[here](https://github.com/noaa-psd/UFS-RNR/blob/feature/bypass_failures/cylc/runtime/README.md). The
`state` may be any acceptable value listed
[here](https://cylc.github.io/cylc-doc/stable/html/running-suites.html#task-states-explained). The
`cycle` attribute is the respective forecast cycle assuming the UNIX
POSIX convention `%Y%m%d%H%M%S`. Finally, the `depends` attribute is
an optional attribute specifying the path to a YAML-formatted file
containing the UFS-RNR Cylc parent task and the respective parent
task's child (e.g., downstream) tasks. And example can be found
[here](https://github.com/noaa-psd/UFS-RNR/blob/feature/bypass_failures/cylc/runtime/depends.UFSRNRv1.ufsp5.yaml).

### Restarting a Stopped UFS-RNR Cylc Suite

It is often useful to shutdown a Cylc suite for various reasons, most
notably during RDHPCS maintenance periods. In order to restart the
respective UFS-RNR Cylc suite, the following can be done:

`user@host:$ cylc restart <experiment_name>`

### Continuing a UFS-RNR Experiment

An example, a completed UFS-RNR experiment directory tree will
resemble the following:

~~~
.
├── cylc
│   ├── cylc_graph.err
│   ├── cylc_graph.out
│   ├── cylc_register.err
│   ├── cylc_register.out
│   ├── cylc_run.err
│   ├── cylc_run.out
│   ├── directives
│   │   ├── bkgrd_forecast.task
│   ├── experiment.rc
│   ├── platform.rc
│   ├── suite.rc
│   ├── tasks.rc
│   ├── UFSRNR_FORECAST
│   │   ├── cylc-suite.db -> log/db
│   │   ├── log
│   │   │   ├── db
│   │   │   ├── job
│   │   │   │   ├── 20160101T0000Z
│   │   │   │   │   ├── bkgrd_forecast
│   │   │   │   │   │   ├── 01
│   │   │   │   │   │   │   ├── job
│   │   │   │   │   │   │   ├── job-activity.log
│   │   │   │   │   │   │   ├── job.err
│   │   │   │   │   │   │   ├── job.out
│   │   │   │   │   │   │   └── job.status
│   │   │   │   │   │   └── NN -> 01
│   │   │   ├── suite
│   │   │   │   ├── log -> log.20210903T141554Z
│   │   │   │   ├── log.20210902T021020Z
│   │   │   │   ├── log.20210902T145040Z
│   │   │   │   └── log.20210903T141554Z
│   │   │   └── suiterc
│   │   │       ├── 20210902T021020Z-run.rc
│   │   │       ├── 20210902T141539Z-reload.rc
│   │   │       └── 20210902T145040Z-restart.rc
│   │   ├── share
│   │   ├── suite.rc.processed
│   │   └── work
│   │       ├── 20160101T0000Z
│   ├── UFSRNR_FORECAST.graph.cycling.png
│   ├── UFSRNR_FORECAST.graph.final.png
│   └── UFSRNR_FORECAST.graph.initial.png
└── UFSRNR_FORECAST.info
~~~

In order to continue a completed experiment beyond the final forecast
cycle specified in the YAML-formatted experiment configuration file,
the user must do collect the `com` directory archive file for the
final forecast cycle (typically from an AWS s3 bucket) and stage it
beneath the experiment top-level directory. The following example
assumes that the user is attempting to continue an experiment on the
supported RDHPCS platforms and that the `<experiment_name>` is
`UFSRNR_FORECAST`.

~~~
user@host:$ cd /path/to/the/experiment/UFSRNR_FORECAST
user@host:$ module load aws-utils
user@host:$ aws s3 cp s3:/bucket/object_path/gzipped_tarball . --no-sign-request
user@host:$ tar -zxvf gzipped_tarball 
~~~

The updated directory structure should now resemble the following:

~~~
├── com
│   └── 20160131180000
│   │   ├── forecast
│   │   ├── gsi
│   │   ├── post
├── cylc
│   ├── cylc_graph.err
│   ├── cylc_graph.out
│   ├── cylc_register.err
│   ├── cylc_register.out
│   ├── cylc_run.err
│   ├── cylc_run.out
│   ├── directives
│   │   ├── bkgrd_forecast.task
│   ├── experiment.rc
│   ├── platform.rc
│   ├── suite.rc
│   ├── tasks.rc
│   ├── UFSRNR_FORECAST
│   │   ├── cylc-suite.db -> log/db
│   │   ├── log
│   │   │   ├── db
│   │   │   ├── job
│   │   │   │   ├── 20160101T0000Z
│   │   │   │   │   ├── bkgrd_forecast
│   │   │   │   │   │   ├── 01
│   │   │   │   │   │   │   ├── job
│   │   │   │   │   │   │   ├── job-activity.log
│   │   │   │   │   │   │   ├── job.err
│   │   │   │   │   │   │   ├── job.out
│   │   │   │   │   │   │   └── job.status
│   │   │   │   │   │   └── NN -> 01
│   │   │   ├── suite
│   │   │   │   ├── log -> log.20210903T141554Z
│   │   │   │   ├── log.20210902T021020Z
│   │   │   │   ├── log.20210902T145040Z
│   │   │   │   └── log.20210903T141554Z
│   │   │   └── suiterc
│   │   │       ├── 20210902T021020Z-run.rc
│   │   │       ├── 20210902T141539Z-reload.rc
│   │   │       └── 20210902T145040Z-restart.rc
│   │   ├── share
│   │   ├── suite.rc.processed
│   │   └── work
│   │       ├── 20160101T0000Z
│   ├── UFSRNR_FORECAST.graph.cycling.png
│   ├── UFSRNR_FORECAST.graph.final.png
│   └── UFSRNR_FORECAST.graph.initial.png
└── UFSRNR_FORECAST.info
~~~

Next, the user must modify the `cylc/experiment.rc` file, specifically
the `FINAL_CYCLE_POINT` attribute. For example, if the experiment had
been previously configured to end at 1800 UTC on 31 January 2016, the
`FINAL_CYCLE_POINT` attribute would be as follows:

`{% set FINAL_CYCLE_POINT = "20160131T180000" %}`

The user may decide to continue the experiment for another month
(i.e., until 1800 UTC 29 February 2016). In that case, the attribute
would be as follows:

`{% set FINAL_CYCLE_POINT = "20160229T180000" %}`

In order to initialize from the final warm start cycle (e.g.,
`20160131T180000`), the user would do as follows:

`user@host:$ cylc run --warm UFSRNR_FORECAST 20160201T0000Z`

where `20160201T0000Z` is the first warm-start cycle for the
continuation of the previous experiment.

# Resetting UFS-RNR Experiments When Cylc Tasks Fail to Submit

Instances when Cylc attempted to submit a UFS-RNR task fail, although
infrequent, can occur. In the following example, we will assume that
the `staging_fetch_atmosobs` task cannot be automatically
(re)submitted by Cylc or manually triggered by the user. In order to
resolve this, do as follows (we assume that the `<experiment_name>` is
`UFSRNR_FORECAST`).

~~~
user@host:$ cd /path/to/the/experiment/UFSRNR_FORECAST/cylc/UFSRNR_FORECAST/log/job/%Y%m%dT%H%MZ/
user@host:$ rm -rf staging_fetch_atmosobs
user@host:$ cylc restart UFSRNR_FORECAST
user@host:$ cylc trigger UFSRNR_FORECAST staging_fetch_atmosobs.%Y%m%dT%H%MZ
~~~

In the above example, `%Y%m%dT%H%MZ` is the Cylc `<DTG>` timestamp
format. The commands accomplish the following. First, the offending
UFS-RNR task Cylc job directory is removed for the respective forecast
cycle. Next, the Cylc workflow is restarted. Finally, the task that
had previously failed to submit is manually triggered to submit again.