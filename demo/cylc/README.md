# UFS Engines Cylc Demo Application

The provided files constitute the configuration of a Cylc engine
workflow application. The example corresponds to a HELLO WORLD
application and may be used to construct more complicated Cylc engine
application workflows.

## HELLO WORLD Demo Configuration Files

<div align="center">

| Configuration File | Description |
| :-------------: | :-------------: |
| [`environment.rc`](environment.rc) | <div align="left">This Jinja2-formatted file contains default environment variables for the respective Cylc application/experiment. </div> |
| [`environment.yaml`](environment.yaml) | <div align="left">This YAML-formatted file contains environment variables specific to a specific Cylc engine application/experiment; the respective environment variables will be appended to the Cylc engine environment.rc Jinja2-formatted file. </div> |
| [`graph.rc`](graph.rc) | <div align="left">This Jinja2-formatted file contains the Cylc application/experiment workflow graph; Cylc documentation concerning the construction of Cylc engine application workflows (i.e., graphs) can be found [here](https://tinyurl.com/cylc-graphs). </div> |
| [`runtime.rc`](runtime.rc) | <div align="left">This Jinja2-formatted file contains the runtime instructions for all applications available to a Cylc engine application/experiment; Cylc documentation concerning the construction of Cylc engine application run-time task attributes can be found at [here](https://tinyurl.com/cylc-runtime).  </div> |
| [`suite.rc`](suite.rc) | <div align="left">This Jinja2-formatted file contains Cylc engine suite configuration; this file is (most likely) generic for all Cylc engine applications; Cylc ocumentation regarding how to configure Cylc engine suites can be found [here](https://tinyurl.com/cylc-suite). </div> | 
| [`tasks.yaml`](tasks.yaml) | <div align="left"> This YAML-formatted file contains the respective task attributes as a function of the respective platform scheduler (e.g., SLURM, PBS, SGE, etc.,); this configuration example is specific to the RDHPCS-Hera platform. </div> | 

</div>