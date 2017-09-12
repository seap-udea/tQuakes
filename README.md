# tQuakes
Earthquakes and Tides

Developed by [Jorge
I. Zuluaga](mailto:jorge.zuluaga@udea.edu.co), [Gloria
Moncayo](mailto:gloria.moncayo@udea.edu.co), [Gaspar
Monsalve](mailto:gmonsalvem@unal.edu.co) [)] 2016.

Presentation
------------

**tQuakes** is a project of the *Solar, Earth and Planetary Physics
Group (SEAP)* of the Institute of Physics (University of Antioquia) in
Medellin (Colombia), in collaboration with the Colombia's National
University.

**tQuakes** (Earthquakes and Tides) is an information platform
intended to explore the relationship between the lunisolar tides and
the triggering of earthquakes.

It combines a huge (and growing) database of Earthquakes around the
globe, with a specialized set of analytical tools able to: 1)
calculate the amplitude of the lunisolar tide at the time and place
where the earthquakes happened and 2) filter, analyse and perform
advanced graphical representations of the earthquake dataset and other
analytical products obtained from them.

**tQuakes** is not only a databased with some related analytical
products. It also provide on-line computational capabilities, provided
by an scalable scavenging grid of Linux servers, able to speed-up the
complex analysis required to study the potential relationship between
tides and seismicity.

Getting a copy
--------------

There are two type of **tQuakes** repositories: ``master`` and
``station``. 

``master`` is the repository containing all the files required to
install a database server. A ``master`` repository should be installed
in the apache root directory:

```
$ cd /var/www/html
$ git clone --branch master http://github.com/seap-udea/tQuakes.git
```

The ``station`` repository is that containing the required files for a
calculation station.  It could be installed on any directory on the machine:

```
$ git clone --branch station --single-branch http://github.com/seap-udea/tQuakes.git
```

or if you are a developer:

```
$ git clone --branch station --single-branch git@github.com:seap-udea/tQuakes.git
```

after properly set up the keys.

tQuakes server
--------------

After obtaining a copy of the ``master`` branch (see previous
section) you need to install all the required packages to run the
analytical tools of **tQuakes**.

Before installing the master, copy the file ``configuration.in`` as
``configuration`` and set the variables: HOMEDIR (it should have more
than 200GB available), DBPASSWORD (password for the tquakes user, see
db/user.sql file), EMAIL_USERNAME, EMAIL_PASSWORD (this the google
account information required to send e-mail notifications), WEBSERVER,
DATASERVER.

Once the previous variables are set run the installation script (the
master only works on Linux Debian machines):

```
# cd /var/www/html/tQuakes
# ./install-full.sh
```

After installation, the server will have:

- All the third-party packages required for the operation of the
  **tQuakes** server (e.g. mysql-server python-mysqldb python-setuptools
  gnuplot-x11 apache2 php5 php5-mysql wget links p7zip
  python-mpltoolkits.basemap python-setuptools). You should pay
  particular attention to mysql server root password.

- ``ETERNA33`` installed at the root directory.

- Package ``SpiceyPy`` installed (see ``python -c "import spiceypy"``).

- A new user ``tquakes`` created in the home directory. 

- Database ``tQuakes`` created in the mysql server.

- And the **tQuakes** server website running and up.

Before starting any computing station you should be sure that all the
earth quakes in the database are reset and ready to be analysed:

```
# make resetquakes
```

This operation may take a while.  Be patient.

If you want to enable the server site to perform calculations of
custom earthquakes you should start the calculation daemon:

```
# make start
```

Starting with a calculation station
-----------------------------------

Once a server is installed and configured you may start installing and
running calculation stations.

After obtaining a copy of the ``station`` branch (see previous
section) you need to install all the required packages to run the
analytical tools of **tQuakes**.

Before proceeding with the installation you will need to copy the file
``configuration.in`` as ``configuration`` and set up the server to
which the station will be providing computing time.

The station only works on Linux Debian machines:

```
$ cd tQuakes
$ ./install.sh
```

Once the software is installed you should pre register your station running:

```
$ python tquakes-sation.py

Station properties:
        Station ID: 007F0100B4317B
        Architecture: Linux urania 4.2.0-35-generic 40~14.04.1-Ubuntu SMP Fri Mar 18 16:37:35 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
        Number of processors: 3
        RAM memory: 16003
        Mac Address: a4:6d:32:c5:82:45

Your station has been preregistered.  Please go to 'http://urania.udea.edu.co/tQuakes/index.php?if=register' to finish the regsitration of the calculation station.

STATION ID: 007F0100B2124124

STATION PUBLIC KEY:

ssh-rsa AAAAB3NzaC1yc2sdafasfAASDASDDU/l1vmEJM5O43I7P2FEgluRl8fGKZ7RUJZGMRYtQkF/mD8qGjGvUQxze49U8/m7b3IjJXzcLjJRbpRffWzEQWLuedeD5YCx6fO1Pj5ldw1m9WQtk3TaHqhoVp37v3WCbMNYbPAm43j4wrkfKGs+HGmXiRnAAO3lWZpw9HO1pWPI99glX3Vs324ovweKfgwXO12DUP0Pb5jYpFNi/uOvOtg4x8ygTevMaUxAhp1pxP6LJi+03v/fIDfeR93YaAexhCvxkzfRfR16t17DhT7ozEimPCkFoD9jH8wIVFf2O9foik2XMxcw5tluYTh+Tx6mgSmrBezCi7pllR6bg6s5K7 root@urania
```

The Station ID and the PUBLIC KEY will be required for registering the
machine in the tQuakes server.

Once a station is registered the manager of the corresponding
**tQuakes** server needs to enable the station by setting the
``Receiving`` parameter in the Station section of the **tQuakes**
website.

To test if the station is properly working run:


```
$ python tquakes-teststation.py
**************************************************
RUNNING tquakes-test
**************************************************
Testing Eterna...
        Eterna is running.
Testing connection with webserver...
        Connection established with server.
Testing database connection...
        Database query working.
Testing database connection...
        Server is receiving from this station.
Testing ssh connection...
        Succesful connection.
ALL TEST PASSED.
```

If all the tests are passed you may be interested on testing if the
whole analysis pipeline is working.  This is done by running:

```
$ cp common common.save && echo "NUMQUAKES=1;" >> common
$ python tquakes-pipeline.py
```

If the pipeline is working you will see how the earthquake is analysed
and the products submitted to the server:

```
**************************************************
RUNNING tquakes-prepare
**************************************************
Searching fetched quakes...
        1 quakes found...
Preparing quake 1 '0017TFZ'
        Locking quake
        Starting date:  2014-06-27 11:53:28
        Eterna files generated...
**************************************************
RUNNING tquakes-eterna
**************************************************
Searching prepared quakes...
        1 prepared quakes found...
Running Eterna for quake 1 '0017TFZ'
        Locking quake
        Starting time:  1470784199.89

        End time:  1470784205.25
        Time elapsed:  5.3681871891
        Reporting calculations...
        Quake done.
**************************************************
RUNNING tquakes-analysis
**************************************************
Searching calculated quakes...
        1 calculated quakes found...
Analysing quake 1 '0017TFZ'
        Starting time:  1470784205.38
        End time:  1470784207.84
        Time elapsed:  2.45757603645
        Reporting calculations...
**************************************************
RUNNING tquakes-submit
**************************************************
Station enabled.
Searching calculated quakes...
        1 analysed quakes found...
Submitting quake 1 '0017TFZ'
        Locking quake
        Starting time:  1470784207.97
0017TFZ.conf
0017TFZ-analysis.tar.7z
0017TFZ-eterna.tar.7z
        End time:  1470784208.16
        Time elapsed:  0.186028003693
        Reporting submission...
        Quake done.
```

After leaving the test recall to recover the common file to the original:

```
$ cp common.save common
```

If everything is working properly you may start the **tQuakes** daemon:

```
$ make start
```

If DOSEMU fails please change the following in the /etc/dosemu/dosemu.conf:
   
```
   $_layout="es-latin1"
   $_cpu_emu="full"
```

Instructions for the contributor
--------------------------------

1. Generate a public key of your account at the client where you will
   develop contributions:
   
   ```
   $ ssh-keygen -t rsa -C "user@email"
   ```

2. Upload public key to the github Seap-Udea repository (only authorized
   for the Seap-Udea repository manager), https://github.com/seap-udea.

3. Configure git at the client:

   ```
   $ git config --global user.name "Your Name"
   $ git config --global user.email "your@email"
   ```

4. Get an authorized clone of the project:

   ```
   $ git clone git@github.com:seap-udea/tQuakes.git
   ```

5. [Optional] Checkout the branch you are interested in
   (e.g. <branch>):

   ```
   $ git checkout -b <branch> origin/<branch>
   ```

6. Checkout back into the ``master``:

   ```
   $ git checkout master
   ```

Licensing
---------

This project must be used and distributed under the [GPL License
Version 2] (http://www.gnu.org/licenses/gpl-2.0.html).

**tQuakes** has been developed under the principles of the [copyleft
philosophy](http://en.wikipedia.org/wiki/Copyleft) `[)]`.

All wrongs reserved to [Jorge
I. Zuluaga](mailto:jorge.zuluaga@udea.edu.co), [Gloria
Moncayo](mailto:gloria.moncayo@udea.edu.co) and [Gaspar
Monsalve](mailto:gmonsalvem@unal.edu.co)
