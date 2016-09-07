#!/usr/bin/env python

"""
Media class. Data structure to select tracks to playlist.
"""

from mongokit import *
import datetime
import random
from collections import OrderedDict
from Queue import Queue
import time
from multiprocessing.synchronize import BoundedSemaphore
from threading import Thread
import uuid

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"


class Buffer(Base):

    queue = OrderedDict({})

    def __init__(self, stream_id, history, playlist, observers):
        super(Buffer, self).__init__()

        self.stream_id = stream_id
        self.observers = observers
        self.history = history
        self.playlist = playlist
        self.queue = OrderedDict({})
        self.lock = BoundedSemaphore(value=1)

        while not self.is_full():
            self.lock.acquire()
            t = self.playlist.get_track()
            self.__add_track(t)

            self.lock.release()

    def update(self, medias):
        self.lock.acquire()
        del self.queue
        self.queue = OrderedDict({})
        for media in medias:
            self.__add_track({
                "artist": media["artist"],
                "album": media["album"],
                "_id": media["_id"],
                "file_id": media["file_id"],
                "title": media["title"],
                "duration": media["tags"]["duration"],
                })
        self.lock.release()

        return True


    def get_track(self):
        self.lock.acquire()

        while not self.is_full():
            self.__add_track(self.playlist.get_track())

        items = self.queue.items()
        track = self.get_first(items)
        if not track:
            return None
        key = track[0]
        track = track[1]
        self.current_track_serialized = track
        self.current_track_serialized["_id"] = unicode(self.current_track_serialized["_id"])
        self.current_track_serialized["started"] = time.time()
        self.current_track_serialized["position"] = 0
        # self.observers.notify({
        #     "playing": self.current_track_serialized
        # })
        del self.queue[key]

        self.history.add(track)
        self.lock.release()
        return track

    @asynchronous
    def notify_current_track(self, respond):
        if hasattr(self, 'current_track_serialized'):
            self.current_track_serialized["position"] = time.time()-self.current_track_serialized["started"]
            yield task(self.call, self.observers.notify, message={
                "playing": self.current_track_serialized
            }, unblock=True)

            # yield task(self.query, self.db.streams.update, {  "_id": ObjectId(self.stream_id) },
            #            {  "$set": {"current": self.current_track_serialized} })

        respond(None)


    def get_first(self, iterable, default=None):
        if iterable:
            for item in iterable:
                return item
        return default

    def __add_track(self, track):
        id = self.__get_id()
        self.queue[id] = track
        return id

    def is_full(self):
        return len(self.queue) >= 6

    def __get_id(self):
        # now = datetime.datetime.now()
        return uuid.uuid4()

    def __wait_until(self, some_predicate, timeout, period=0.25):
        must_end = time.time() + timeout
        while time.time() < must_end:
            if some_predicate(): return True
            time.sleep(period)
        return False

    @asynchronous
    def notify_buffer_update(self, respond):
        buffer = []
        for q in self.queue:
            track_serialized = self.queue[q]
            track_serialized["_id"] = unicode(track_serialized["_id"])
            buffer.append(self.queue[q])

        if self.playlist.__class__.__name__ == "RandomPlaylist":
            selection = "shuffle"
        else:
            selection = "sequence"

        yield task(self.call, self.observers.notify, message={
            "buffer_update": buffer,
            "selection": selection
        }, unblock=True)
        respond(None)

    def show(self):
        for q in self.queue:
            print unicode(self.queue[q])




class History(Base):

    def __init__(self, observers):
        super(History, self).__init__()

        self.size = 100
        self.q = Queue(self.size)
        self.observers = observers


    def add(self, track):
        if self.q.qsize() >= self.size - 1:
            self.q.get()


        # self.q.put({
        #     "artist": track.parent.parent.name,
        #     "album": track.parent.name,
        #     "_id": track.id,
        #     "file_id": track.file_id,
        #     "title": track.name,
        #     "duration": track.duration
        # })

        self.q.put({
            "artist": track["artist"],
            "album": track["album"],
            "_id": track["_id"],
            "file_id": track["file_id"],
            "title": track["title"],
            "duration": track["duration"]
        })



    def clear(self):
        with self.q.mutex:
            self.q.queue.clear()

    @asynchronous
    def notify_previous_update(self, respond):
        buffer = []
        i = 0
        for q in reversed(list(self.q.queue)):
            track_serialized = q
            track_serialized["_id"] = unicode(track_serialized["_id"])
            buffer.append(track_serialized)
            # buffer.insert(0, (track_serialized))
            i+=1
            if i >= 5: break
        yield task(self.call, self.observers.notify, message={
            "previous_update": buffer
        }, unblock=True)

        respond(None)


class Randomizer:

    def randomize_ordered_dict(self, ordered_dict):
        items = ordered_dict.items()
        random.shuffle(items)
        return OrderedDict(items)

class Playlist:


    # current_track = 0

    def __init__(self, medias, observers):
        self.tracks = OrderedDict({})
        self.current_track = -1
        for media in medias:
            if not media["_id"] in self.tracks:
                self.__add(media)

    def set_current_track_if_possible(self, new_current_track):
        if len(self.tracks.items())-1 >= new_current_track:
            self.current_track = new_current_track

    def __add(self, media):
        track = {
            "artist": media["artist"],
            "album": media["album"],
            "_id": media["_id"],
            "file_id": media["file_id"],
            "title": media["title"],
            "duration": media["tags"]["duration"],
        }
        self.tracks[media["_id"]] = track

    def get_track(self):
        if self.current_track == len(self.tracks.items())-1:
            self.current_track = 0
        else:
            self.current_track += 1

        if not self.current_track < len(self.tracks.items()):
            return None

        print unicode(self.current_track)+" "+unicode(self.tracks.items()[self.current_track][1]["_id"])

        return self.tracks.items()[self.current_track][1]

    def add_track(self, media):
        self.__add(media)


    def show(self):
        for track in self.tracks:
            print unicode(track)+" "+unicode(self.tracks[track])





class RandomPlaylist(Randomizer):


    def __init__(self, medias, observers):
        self.artists = OrderedDict({})
        self.history = None
        self.lock = BoundedSemaphore(value=1)

        for media in medias:
            self.__add(media)

        # self.show()
        self.shuffle()

    def __add(self, media, played = 0):
        self.lock.acquire()
        if not media["artist"] in self.artists:
            artist = Artist(media["artist"])
            artist.parent = self
            self.artists[media["artist"]] = artist
        else:
            artist = self.artists[media["artist"]]

        if not media["album"] in self.artists[media["artist"]].albums:
            album = Album(media["album"])
            album.parent = artist
            self.artists[media["artist"]].albums[media["album"]] = album
        else:
            album = self.artists[media["artist"]].albums[media["album"]]

        if not media["_id"] in self.artists[media["artist"]].albums[media["album"]].tracks:
            media_id = unicode(media["_id"])
            track = Track(media_id, media["file_id"], media["title"], media["tags"]["duration"], media)
            track.played = played
            track.parent = album
            self.artists[media["artist"]].albums[media["album"]].tracks[media_id] = track

            self.artists[media["artist"]].tracks_count += 1
            self.artists[media["artist"]].played += played
            self.artists[media["artist"]].albums[media["album"]].tracks_count += 1
            self.artists[media["artist"]].albums[media["album"]].played += played

            for i in range(played):
                track.play()
        self.lock.release()


    def shuffle(self):
        self.randomize_ordered_dict(self.artists)
        for artist in self.artists:
            self.artists[artist].shuffle()

    def apply_history(self, history):
        """
        Try to find track and play it so it would not be played next time
        """
        with history.q.mutex:
            items = list(history.q.queue)

        for media in items:
            if media["artist"] in self.artists:
                artist = self.artists[media["artist"]]
            else:
                continue

            if media["album"] in artist.albums:
                album = artist.albums[media["album"]]
            else:
                continue

            if media["_id"] in album.tracks:
                track = artist.albums[media["album"]].tracks[media["_id"]]
            else:
                continue

            track.play()

        self.history = history

    def get_track(self):

        self.lock.acquire()
        artist = self.get_first(self.artists.items())
        if artist is None:
            return None
        artist = self.artists.items()[0][1]

        album = self.get_first(artist.albums.items())
        if album is None:
            return None
        album = artist.albums.items()[0][1]

        track = self.get_first(album.tracks.items())
        if track is None:
            return None
        track = album.tracks.items()[0][1]

        # print len(self.artists)
        # self.show()
        # print "choosing "+str(track.id)

        # print "artist play index "+str(track.parent.parent.play_index)+" album play index "+str(track.parent.play_index)+" track played"+str(track.played)

        play = track.play()
        self.lock.release()
        return play

    def add_track(self, media):

        artist = self.get_first(self.artists.items())
        if artist is None:
            return None
        artist = self.artists.items()[0][1]

        album = self.get_first(artist.albums.items())
        if album is None:
            return None
        album = artist.albums.items()[0][1]

        track = self.get_first(album.tracks.items())
        if track is None:
            return None
        track = album.tracks.items()[0][1]

        self.__add(media, track.played)


    def get_first(self, iterable, default=None):
        if iterable:
            for item in iterable:
                return item
        return default


    def show(self):
        for artist in self.artists:
            print "-- Artist "+unicode(self.artists[artist].played)+"/"+unicode(self.artists[artist].tracks_count)+"="+unicode(self.artists[artist].play_index)+self.artists[artist].name
            for album in self.artists[artist].albums:
                print "---- Album "+unicode(self.artists[artist].albums[album].played)+"/"+unicode(self.artists[artist].albums[album].tracks_count)+"="+unicode(self.artists[artist].albums[album].play_index)+" "+album
                for track in self.artists[artist].albums[album].tracks:
                    print "------ Track "+unicode(self.artists[artist].albums[album].tracks[track].played)+" "+self.artists[artist].albums[album].tracks[track].id



    def update(self):
        self.artists = OrderedDict(sorted(self.artists.items(), key=lambda t: t[1].play_index))



class Artist(Randomizer):

    def __init__(self, name):
        self.name = name
        self.albums = OrderedDict({})
        self.play_index = float(0)
        self.played = 0
        self.tracks_count = 0
        self.parent = None

    def update(self):
        self.played += 1
        self.play_index = float(self.played) / float(self.tracks_count)
        self.albums = OrderedDict(sorted(self.albums.items(), key=lambda t: t[1].play_index))
        if int(self.play_index) == self.play_index:
            self.shuffle()
        self.parent.update()

    def shuffle(self):
        self.randomize_ordered_dict(self.albums)
        for album in self.albums:
            self.albums[album].shuffle()


class Album(Randomizer):

    def __init__(self, name):
        self.name = name
        self.tracks = OrderedDict({})
        self.play_index = float(0)
        self.played = 0
        self.tracks_count = 0
        self.parent = None

    def update(self):
        self.played += 1
        self.play_index = float(self.played) / float(self.tracks_count)
        self.tracks = OrderedDict(sorted(self.tracks.items(), key=lambda t: t[1].played))
        if int(self.play_index) == self.play_index:
            self.shuffle()
        self.parent.update()

    def shuffle(self):
        self.randomize_ordered_dict(self.tracks)

class Track:

    def __init__(self, id, file_id, name, duration, media):
        self.id = unicode(id)
        self.file_id = unicode(file_id)
        self.played = 0
        self.name = name
        self.duration = duration
        self.media = media

    def play(self):
        # if not self.parent.parent.parent.history is None:
        #     self.parent.parent.parent.history.add(self)
        self.update()
        return {
            "artist": self.parent.parent.name,
            "album": self.parent.name,
            "_id": self.id,
            "file_id": self.file_id,
            "title": self.name,
            "duration": self.duration,
        }

    def update(self):
        self.played += 1
        self.parent.update()
