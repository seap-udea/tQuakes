# tQuakes
Earthquakes and Tides

Developed by [Jorge
I. Zuluaga](mailto:jorge.zuluaga@udea.edu.co),[Gloria
Moncayo](mailto:gloria.moncayo@udea.edu.co), [Gaspar
Monsalve](mailto:gmonsalvem@unal.edu.co)

Presentation
------------

*tQuakes* is a project of the **Solar, Earth and Planetary Physics
Group (SEAP)** of the Institute of Physics (University of Antioquia)
in Medellin (Colombia), in collaboration with the Colombia's National
University.

*tQuakes* (Earthquakes and Tides) is an information platform intended
to explore the relationship between the lunisolar tides and the
triggering of earthquakes. 

It combines a huge (and growing) database of Earthquakes around the
globe, with a specialized set of analytical tools able to calculate
the amplitude of the lunisolar tide at the time and place where the
earthquakes happened and to filter, analyse and perform advanced
graphical representations of the earthquake dataset and other
analytical products obtained from them.

*tQuakes* is not only a databased with some related analytical
products. It also provide on-line computational capabilities, provided
by an scalable scavenging grid of Linux servers, able to speed-up the
complex analysis required to study the potential relationship between
tides and seismicity.

In this site you will find or be able to:

Browse the Earthquakes database. Detailed information about each earthquake is provided (location by coordinates, location by city, province and country, magnitude, depth date and time, etc.). You will be able to perform simple and advanced queries on the database and download subsets.
Information on tides at earthquakes location and time. Get information about tides at the times when the earthquakes in database happen. Here you will find precalculated values and phases of tides for most of the earthquakes in our database. tQuakes provide values and phases for the most important phase components (vertical displacement, gravitational acceleration, horizontal and vertical strain, etc.)
Calculate tides at any location and time. We provide a simple web interface to ETERNA, a software to calculate solid tides provided location, depth and tiem.
Access to analytical products. Database administrators perform analysis on the database to study the statistical correlation between seismicity and tides. Here you will find some analytical products for the database.
Download tQuakes. tQuakes is an open source project. You may download the full tQuakes server, including a previously feed database or the tQuakes working station if you want to provide computing time to the project.
Get a complete list of references in the field. We provide here the most complete list of peer reviewed papers, books, thesis and other documents related directly or indirectly to the investigation on the possible connection between tides and seismic activity.

tQuakes.

Getting a copy
--------------

To get a copy of the newest version of this project just execute:

```
$ git clone --branch master http://github.com/seap-udea/tQuakes.git
```

If you want to get a different branch of the project just change
"master" by the name of the branch.

This is the developer copy.  You may also obtain the latest release of
the installable package, available in the `dist` folder.

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

6. Checkout back into the master:

   ```
   $ git checkout master
   ```

Licensing
---------

This project must be used and distributed under the [GPL License
Version 2] (http://www.gnu.org/licenses/gpl-2.0.html).

The symbol `[)]` means that it has been developed under the principles
of the [copyleft philosophy](http://en.wikipedia.org/wiki/Copyleft).

All wrongs reserved to [Jorge
I. Zuluaga](mailto:jorge.zuluaga@udea.edu.co), [Gloria
Moncayo](mailto:gloria.moncayo@udea.edu.co) and [Gaspar
Monsalve](mailto:gmonsalvem@unal.edu.co)
