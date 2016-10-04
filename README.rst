===============
Runner-Reloader
===============

Runner for development code

.. code:: shell

    $ rr --help
    usage: rr [-h] [--interval INTERVAL] cmd [args [args ...]]

    Runner-Reloader for development

    positional arguments:
      cmd                   command
      args                  arguments

    optional arguments:
      -h, --help            show this help message and exit
      --interval INTERVAL, -i INTERVAL
                            interval for check

For example
===========

.. code:: shell

    $ rr my-app serve --listen 0.0.0.0:8080

This command launch ``my-app serve --listen 0.0.0.0:8080``.
If some files in current dirrectory was changed, application authomatically restarted.

This is usable for development docker containers.


Installation
============

.. code:: shell

    $ pip install rr
