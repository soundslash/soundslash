#!/usr/bin/env python

"""
GridFS class.
"""

from mongokit import *
import datetime

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class File(Document):

    # __collection__ = 'servers'
    __database__ = 'pipeline'

    gridfs = {'files':['source', 'template']}

    structure = {

    }

    default_values = {

        }
