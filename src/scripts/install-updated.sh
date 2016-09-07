

# src
vim /etc/apt/sources.list
deb http://nginx.org/packages/debian/ squeeze nginx
deb-src http://nginx.org/packages/debian/ squeeze nginx
apt-get update
wget wget http://snapshot.debian.org/archive/debian/20110406T213352Z/pool/main/o/openssl098/libssl0.9.8_0.9.8o-7_amd64.deb
dpkg -i libssl0.9.8_0.9.8o-7_amd64.deb
apt-get install nginx git screen

apt-get install python-2.7
apt-get install python
apt-get install tornado
apt-get install pip
apt-get install python-tornado
apt-get install python-pip
pip install motor
apt-get install gcc
apt-get install g++
apt-get install python-dev
apt-get install g++
pip install motor
pip install motor --upgrade
apt-get install futures
pip install futures
apt-get install pygst
apt-get install python-gstreamer
apt-get install python-gst0.10
apt-get install gstreamer-plugins-base
apt-get install libgstreamer-plugins-base0.10
apt-get install mc

apt-get install sudo
vim /etc/sudoers
www ALL= NOPASSWD: /etc/init.d/soundslash-web, /etc/init.d/soundslash-pipeline, /etc/init.d/soundslash-auth, /etc/init.d/icecast2

#apt-get install mongo
#apt-get install mongodb
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update
sudo apt-get install -y mongodb-org
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections

> use pipeline
switched to db pipeline
> db.createUser({user: "pipeline", pwd: "horcica7med#vajco1parky", roles: [{role: "readWrite", db: "pipeline"}]})

/etc/init.d/mongod stop
cp -avr /var/lib/mongodb/ /www/mongodb/
rm -rf /var/lib/mongodb/
vim /etc/mongod.conf
dbpath=/www/mongodb
auth = true

apt-get install libjpeg-dev
pip install -I pillow

apt-get install vim
apt-get install soundconverter
apt-get install lame
apt-get install gstreamer0.10-ffmpeg
apt-get install ffmpeg
apt-get install gstreamer0.10-fluendo-mp3
apt-get install gstreamer
apt-get install gstreamer0.10-gnonlin
apt-get install sudo
pip install simplejson
# websocket and websocket-client are coliding
# remove both ant then install websocket-client
pip uninstall websocket
pip uninstall websocket-client
pip install websocket-client

pip install Image
pip install facebook-sdk
pip install unidecode
pip install pydispatch
pip install PyDispatcher
pip install psutil
pip install SoundAnalyse
apt-get install libsndfile1-dev
pip install scikits.audiolab
usermod -a -G icecast www

pip install netifaces




git clone https://github.com/namlook/mongokit.git
cd mongokit
python setup.py install
