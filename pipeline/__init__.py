"""
m2u minimal pipeline

This module contains the necessary pipeline tasks for m2u to function correctly.
These are mainly operations on the file-system.

There are also Program- and maybe Editor- specific pipeline tasks, which will
reside in their own modules, but are referenced through here.

The minimal pipeline is a simple implementation of only the necessary tasks.
The pipeline module can be replaced as long as you provide the required interface
for m2u. To strap your own pipeline into m2u, set the "[General] PipelineModule"
value in the settings file to point to your pipelines interface-module for m2u.
Alternatively you can overwrite the _initPipeline() function in core.py or load
m2u from within your pipeline and do the whole initialization yourself.

"""

from m2u.pipeline.pipelineInterface import *