nvb-client README
==================

# Installation

## Linux

A small Ubuntu 14.04 VPS is used for this section.

First, update: `$ sudo apt-get update && sudo apt-get upgrade`

Second, install the requirements

```
$ sudo apt-get install python3.4 python3-pip git-core libffi-dev libssl-dev build-essential
$ mkdir ~/src && cd ~/src
$ git clone https://github.com/XertroV/nvblib
$ cd nvblib && sudo python3 setup.py install; cd ..
$ git clone https://github.com/richardkiss/pycoin
$ cd pycoin && sudo python3 setup.py install; cd ..
$ git clone https://github.com/XertroV/nvbclient
$ cd nvbclient
$ sudo python3 setup.py develop
```

Finally, initialize the DB and start the webclient. You'll be prompted for a password when you set up the DB, though you are free to change it later in settings.

```
$ initialize_nvb_client_db development.ini

$ pserve development.ini
Starting server in PID 11607.
serving on http://0.0.0.0:6655
```

Now navigate to port 6655 on your IP! Try http://127.0.0.1:6655 on localhost.

To do
-----

* persistent utxos
* track votes (alert of dup?)
* broadcast tx


Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/python setup.py develop

- $VENV/bin/initialize_nvb_client_db development.ini

- $VENV/bin/pserve development.ini

#### Test checklist

[] - item 1
[x] - item 2
