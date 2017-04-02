===============
Runner-Reloader
===============

Runner for development code.


Usage
=====

.. code:: shell

    $ rr --help
    usage: rr [-h] [--interval INTERVAL] [--exclude EXCLUDE]
              [--loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
              ...

    Runner-Reloader for development

    positional arguments:
      command               command

    optional arguments:
      -h, --help            show this help message and exit
      --interval INTERVAL, -i INTERVAL
                            interval for check
      --exclude EXCLUDE, -e EXCLUDE
                            exclude pattern
      --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            loglevel for rr

    $ rr --interval=10 my-app serve --listen=0.0.0.0:8080

This command launch ``my-app serve --listen=0.0.0.0:8080``
and scan current directory for changed files every ten seconds.
If some files was changed, application authomatically restarted.

This is usable for *development* docker containers.


Installation
============

.. code:: shell

    $ pip install rr


Settings
========

File ``.rr`` in current directory parsed for settings.
rr uses the `zini <https://github.com/zzzsochi/zini>`_ library for this.

:command: command for run
:interval: interval between scan directory
:exclude: list of excluded directories for scan
:loglevel: `loglevel <https://docs.python.org/3/howto/logging.html#logging-levels>`_ for rr

Command line arguments has a higher priority than settings.


For example:
~~~~~~~~~~~~

.. code:: ini

    [default]
    command = 'ping 8.8.8.8'
    interval = 5s
    loglevel = 'DEBUG'
    exclude =
        '*/__pycache__'
        '.git'
        'node_modules'
        'build'
        'dist'
