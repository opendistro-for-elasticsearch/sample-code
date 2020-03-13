# MIT License
#
# Copyright (c) 2020 Amazon Web Services
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


'''
Provides the BGGManager class. The BGGManager class is a wrapper around the
boardgamegeek2 API. Init with an ids file, a names file, and a details file.
The instance can optionally download from boardgamegeek, or loaded from disk.
'''


import json
import pickle
from itertools import zip_longest


from boardgamegeek import BGGClient


class BGGManager():
    ''' The BGGManager class is a wrapper around the boardgamegeek2 API. Init
        with an ids file, a names file, and a details file. The instance can
        optionally download from boardgamegeek, or loaded from disk.'''

    def __init__(self, ids_file, names_file, details_file):
        '''ids_file - name of a file with/for BGG ids
           names_file - name of a file with/for BGG game names
           details_file - name of a file with/for BGG game details'''
        self._ids_file = ids_file
        self._ids = None
        self._names_file = names_file
        self._names = None
        self._details_file = details_file
        self._bgg = BGGClient()

    @staticmethod
    def grouper(n, iterable, fillvalue=None):
        '''Turns a flat list into a set of groups of length n. BGGManager uses
           this to group the downloaded ids into batches for retrieval from
           boargamegeek's batch API.
           Example: grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
        '''
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)

    @staticmethod
    def boardgame_to_dict(bg):
        ''' Turns the structure returned by boardgamegeek2 into a dict, suitable
            for uploading to Elasticsearch.
            TODO: there are some deeper substructures - stats and ranks that
                  would be nice to have as well. They don't bear directly, so I
                  have ignored them.

            Initially I was trying to use class introspection to implement this
            but not all of the below are actually attributes of the class. This
            method is messier but actually works.'''
        return {
            "accessory": bg.accessory,
            "alternative_names": bg.alternative_names,
            "artists": bg.artists,
            "bgg_rank": bg.bgg_rank,
            "boardgame_rank": bg.boardgame_rank,
            "categories": bg.categories,
            "comments": bg.comments,
            "description": bg.description,
            "designers": bg.designers,
            "expansion": bg.expansion,
            "families": bg.families,
            "id": bg.id,
            "image": bg.image,
            "implementations": bg.implementations,
            "max_players": bg.max_players,
            "max_playing_time": bg.max_playing_time,
            "mechanics": bg.mechanics,
            "min_age": bg.min_age,
            "min_players": bg.min_players,
            "min_playing_time": bg.min_playing_time,
            "name": bg.name,
            "playing_time": bg.playing_time,
            "publishers": bg.publishers,
            "rating_average": bg.rating_average,
            "rating_average_weight": bg.rating_average_weight,
            "rating_bayes_average": bg.rating_bayes_average,
            "rating_median": bg.rating_median,
            "rating_num_weights": bg.rating_num_weights,
            "rating_stddev": bg.rating_stddev,
            "thumbnail": bg.thumbnail,
            "users_commented": bg.users_commented,
            "users_owned": bg.users_owned,
            "users_rated": bg.users_rated,
            "versions": bg.versions,
            "videos": bg.videos,
            "year": bg.year
        }

    def _download_and_save_games(self):
        ''' Use the API to pull games from boardgamegeek. There isn't a good way
            to search generically, the API requires at least 1 character for the
            wildcard. So I took the approach of wildcarding each letter of the
            alphabet. This misses some games, even some top games, but gets most
            everything.
            Note, since the API is searching across words, there are duplicate
            names and ids downloaded. This is handled with a set() structure to
            hold names and ids.
            Pickles ids and names that it downloads to the names file and ids
            file.'''
        self._ids = set()
        self._names = set()
        small_letters = map(chr, range(ord('a'), ord('z')+1))
        for letter in small_letters:
            things = bgg.search('{}*'.format(letter))
            for thing in things:
                self._ids.add(thing.id)
                self._names.add(thing.name)
        with open(self._ids_file, 'wb') as ids_file:
            pickle.dump(ids, ids_file)
        with open(self._names_file, 'wb') as names_file:
            pickle.dump(names, names_file)

    def _load_saved_games(self):
        '''Loads the pickled game names and ids'''
        with open(self._names_file, 'rb') as names_file:
            self._names = pickle.load(names_file)

        with open(self._ids_file, 'rb') as ids_file:
            self._ids = pickle.load(ids_file)

    def load_game_names_and_ids(self, download=False):
        ''' Entry point for loading game names and ids. Set download=True to use
            the Boardgame Geek APIs to download them fresh, or False to load
            pickled data from a prior run. '''
        if download:
            self._download_and_save_games()
        else:
            self._load_saved_games()

        print('Got {} ids and {} names'.format(len(self._ids), 
                                               len(self._names)))

    def _download_and_save_game_details(self):
        ''' Downloads game details from the BoardgameGeek API. This takes the
            ids and splits them into chunks of 100 so that it can call the BGG
            batch API for retrieval.
            After retrieving the game details, this reformats them as a dict for
            easier transmission to ES.
            I made the decision to store the text JSON of the details instead of
            pickling or storing in some other binary format. This facilitates
            quickly grepping the source data as well as processing to generate
            test sets.
            A bunch of the parameters (e.g. group size) might be better specified
            on the command line. For simplicity, they're hard-coded here.'''
        n = 0
        chunk_size = 100
        with open(self._details_file, 'w') as details_file:
            for chunk in self.grouper(chunk_size, ids, fillvalue=None):
                games = bgg.game_list(game_id_list=list(chunk))
                n += chunk_size
                print('Downloaded {} games.'.format(n))
                for g in games:
                    try:
                        d = self.boardgame_to_dict(g)
                        if d:
                            json.dump(d, details_file)
                            details_file.write('\n')
                    except Exception as e:
                        print('Exception getting details. Skipping "{}".'.format(g.name))

    def _load_saved_game_details(self):
        ''' Loads the game details from the JSON file where they are stored. '''
        self._details = list()
        with open(self._details_file, 'r') as f_in:
            for line in f_in:
                dic = json.loads(line.lstrip().rstrip())
                self._details.append(dic)
        print("Loaded {} game records".format(len(self._details)))

    def load_game_details(self, download=False):
        ''' Entry point for downloading or loading the game details. Specify
            download=True to pull from BGG or download=False to load a previous
            data set. '''
        if download:
            if not self._ids or not self._names:
                # TODO: Better exception
                raise Exception('Can\'t download game details without loading names and ids first!')
            self._download_and_save_game_details()
        else:
            self._load_saved_game_details()

    def game_details(self):
        ''' Iterator over the game details. Details must be loaded first. '''
        if not self._details:
            raise ValueError('Trying to send iterate game details, but none loaded')
        for detail in self._details:
            yield detail

