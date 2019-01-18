DEVELOPERS INFORMATIONS
-----------------------

What is it supposed to do ?
=================

The aim is currently NOT try to offer a full cli for taiga.
This module has three purposes:
- to make some annoying task easier, like moving a task from a user story to
  another, which in taiga UI is pretty painful if they're not in the same
  sprint. or getting a list of all the tasks ready to review for a particular
  sprint.
- In taiga is impossible to have a timeline of the work items. how my
  sprintboard looked like two weeks ago ? What was the status of this task
  yesteday ? taigacli offers a way to take snapshots of the sprint. A snapshot
  stores in a database all the user stories, tasks, issues with a timestamp.
  This database can be queried locally for statistics on the timeline.
- create statistics and informational graphs, like a tree of dependencies for
  the tasks/user stories, using custom attributes.


How Does it do it ?
==================

it uses partially python-taiga (lacks support for epics) to download
information from the main taiga server, and stores them in a database (sqlite ATM)
Then offers the possibility to query this database, using custom queries that
are made avaiable to the main command

The database is flattened as much as possible, there are no foreign keys, and
the aim is not to replicate the taiga database. For example status and users
ids in taiga are directly translated to their names in the database.

The idea is to facilitate the creation of graphs from those data using influxdb

Why aren't you using influxdb directly ?
++++++++++++++++++++++++++++++++++++++++

influxdb was created with graphs in mind. A time series needs a value
somewhere, and the use of tags and field doesn't really cut what this is aiming
to be

Installation
============

git clone https://github.com/
python3 -m virtualenv -p python3 taigacli-venv
cd taigacli-venv
python setup.py develop

Usage
=====

taigacli -h

uses subcommands, only a few are implemented currently, ideas welcome

Adding commands
===============

Add a new file in taigacli/commands/
Look at taigacli/command, class SnapshotCommand for example how to integrate
the command with the parser
Look at taigacli.py, class configuration, section # command for example on how
to integrate the make the command available to the cli

Subcommands are in the same file as the top level commands.

Adding a query
=============

Custom queries are in a separate module taigacli_custom_queries to keep them
separate from the main code, so they can be customized without interfering with
the module
