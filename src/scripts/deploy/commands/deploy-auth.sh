#!/bin/bash
cd soundslash/
git pull
sudo /etc/init.d/icecast2 restart
echo "!"
sudo /etc/init.d/soundslash-auth restart
