# Launching

To launch the available UFS-RNR Cylc applications, do as follows for
the respective supported platform(s).

#### RDHPCS Orion

~~~
user@host:$ module use -a /work/noaa/gsienkf/UFS-RNR/UFS-RNR-stack/modules
user@host:$ module load anaconda3
user@host:$ module load ufsrnr-cylc
user@host:$ cd /path/to/UFS-RNR-package/cylc
user@host:$ python /work/noaa/gsienkf/UFS-RNR/UFS-RNR-stack/ufsrnr-cylc/cylc_run.py --yaml /path/to/UFS-RNR-package/cylc/experiment/experiment.yaml
~~~