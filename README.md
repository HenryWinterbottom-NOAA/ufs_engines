[![License](https://img.shields.io/badge/license-LGPL_v2.1-lightgray)](https://github.com/HenryWinterbottom-NOAA/ufs_engines/blob/develop/LICENSE)
![Linux](https://img.shields.io/badge/linux-ubuntu%7Ccentos-black)
![Python Version](https://img.shields.io/badge/python-3.5|3.6|3.7-blue)

[![Dependencies](https://img.shields.io/badge/dependencies-ufs__pyutils-orange)](https://github.com/HenryWinterbottom-NOAA/ufs_pyutils)

[![Python Coding Standards](https://github.com/HenryWinterbottom-NOAA/ufs_engines/actions/workflows/pycodestyle.yaml/badge.svg)](https://github.com/HenryWinterbottom-NOAA/ufs_engines/actions/workflows/pycodestyle.yaml)

# Disclaimer

The United States Department of Commerce (DOC) GitHub project code is
provided on an "as is" basis and the user assumes responsibility for
its use. DOC has relinquished control of the information and no longer
has responsibility to protect the integrity, confidentiality, or
availability of the information. Any claims against the Department of
Commerce stemming from the use of its GitHub project will be governed
by all applicable Federal law. Any reference to specific commercial
products, processes, or services by service mark, trademark,
manufacturer, or otherwise, does not constitute or imply their
endorsement, recommendation or favoring by the Department of
Commerce. The Department of Commerce seal and logo, or the seal and
logo of a DOC bureau, shall not be used in any manner to imply
endorsement of any commercial product or activity by DOC or the United
States Government.

# Cloning

This repository utilizes several sub-modules from various sources. To
obtain the entire system, do as follows.

~~~
user@host:$ git clone https://github.com/HenryWinterbottom-NOAA/ufs_engines
~~~

# Using Cylc-flow

The Cylc engine version supported by this application is
[v7.9.3](https://github.com/cylc/cylc-flow/releases/tag/7.9.3). The
Cylc engine is install for supportted RDHPCS platforms and may be
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

# Forking

If a user wishes to contribute modifications done within their
respective fork(s) to the authoritative repository, we request that
the user first submit an issue and that the fork naming conventions
follow those listed below.

- `docs/user_branch_name`: Documentation additions and/or corrections for the application(s).

- `feature/user_branch_name`: Additions, enhancements, and/or upgrades for the application(s).

- `fix/user_branch_name`: Bug-type fixes for the application(s) that do not require immediate attention.

- `hotfix/user_branch_name`: Bug-type fixes which require immediate attention to fix issues that compromise the integrity of the respective application(s). 

