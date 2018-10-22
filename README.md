# Doberman Webmonitor #

** D. Masson **

24 August 2018

## Brief ##

The *Doberman Webmonitor* is a Django-based program that monitors an instance of [Doberman slowcontrol](https://github.com/ag-schumann/doberman). Doberman does not need to be running, but this software otherwise doesn't really have much point.

## Prerequisites ##

This code is based on python 3.7 on Ubuntu 18.04. It does not need to be on the same machine as Doberman (or even have access to it), but it must have access to the Doberman database.

## Installation ##
For Ubuntu 18.04.

* Install an environment with the necessary packages: `conda create --name webmonitor python=3.7 pymongo=3.7 django=2.1`
* Make sure the correct environmental variables get loaded with this environment:
    * Go to `$CONDA_PREFIX`
    * If the directories `./etc/conda/activate.d` and `./etc/conda/deactivate.d` don't exist, make them.
    * Make a bash script in each with a name like `env_vars.sh`
    * `activate.d/env_vars.sh`:
```
#!/bin/bash
export MONITOR_URI=<mongo uri>
export DJANGO_KEY=<django key>
```
        * `<mongo uri>` is the MongoDB URI to connect to the database (`mongodb://username:password@host:port/admin` - a read-only account is recommended for this)
        * `<django key>` is the Django key with which your website secures itself
    * `deactivate.d/env_vars.sh`:
```
#!/bin/bash
unset MONITOR_URI
unset DJANGO_KEY
```
* Download this package: `git clone https://github.com/ag-schumann/webmonitor.git`
* Add your host to the `allowed_hosts` entry in `webmonitor/settings.py`

### Apache ###

* `sudo apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3`
