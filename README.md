easyPCE
=======

Don't mess with standard django files and dev standard django files. Templates are self-exp.
Readmes exist in other main directories with information about updating database for each 
semester. We need to figure out how to exclude canceled ones.


Installation
------------

<!-- TODO: Put all of this into a setup.py kind of deal -->

To set up a development environment, make sure you have Python 2,
[memcached][] and [MySQL][] installed. Now, set up and pre-populate the MySQL
database:

[memcached]: https://memcached.org/
[MySQL]: https://dev.mysql.com/doc/refman/5.7/en/installing.html

```shell
$ mysqladmin -u root password 'somepassword'
$ mysql -p -u root PCE_2 < pce/easyPCEdump.sql
```

Then, install all of the Python dependencies:

```shell
$ pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Contributors and Contributing
-----------------------------

easyPCE was originally built by John Whelchel, Yacob Yonas, and Matt Haake as
a COS 333 project. It is now being maintained by Casey Chow.

If you're interested in working on easyPCE, go ahead and fork this repo. This
project utilizes [Github Flow](gh-flow) to manage overlapping contributions.
Essentially, fork this repo, make a new branch, and then Pull Request it onto
the original repo.

[gh-flow]: https://guides.github.com/introduction/flow/