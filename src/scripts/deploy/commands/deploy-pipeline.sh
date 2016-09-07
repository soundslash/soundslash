#!/bin/bash
cd soundslash/
git pull

sudo /etc/init.d/soundslash-pipeline restart
