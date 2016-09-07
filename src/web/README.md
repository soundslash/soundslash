
MongoDB unexpected exit
=======================

rm /var/lib/mongodb/journal/*
mongod --dbpath /var/lib/mongodb/ -repair
chown mongodb /var/lib/mongodb/ -R
chgrp nogroup /var/lib/mongodb/ -R
/etc/init.d/mongodb start

UML
===

pylint
pydot

