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
BGG - Download and search board game data from BoardgameGeek.com

This sample application uses the boardgamegeek2 library (available on PyPi) to 
download names, ids, and full descriptions for board games from 
boardgamegeek.com's API. It uses the es_sink library to send the board game 
details to an Open Distro for Elasticsearch cluster running on localhost. Of 
course, you can change that and send it to any Elasticsearch cluster.

Prerequisite

You must download and install the es_sink library, available in this repo.

Usage

First, run bgg.py to download names and details from boardgamegeek.

```$ python bgg.py --names <file name> --ids <file name> --details-file <file name> --download-ids --download-details```

The ```--names``` parameter lets you specify a file that will hold the names 
from boardgamegeek, the ```--ids``` parameter lets you specify a file to 
hold the boardgamegeek ids, and the ```--details-file``` parameter lets you 
specify a file to hold the game details. Note: these files must be different.

When you're ready to upload to Elasticsearch, run

```$ python bgg.py --names <file name> --ids <file name> --details-file <file name> --send-to-es```

There is currently no command line support for changing the endpoint. You can 
edit the ESDescriptor in es_manager.py to change the destination location, 
authentication method, and ES version. See the __init__ function in 
es_manager.py. See the es_sink library for details on how to change the 
parameters.
'''

import argparse
import json


from bgg_manager import BGGManager
from es_manager import ESManager


def parse_args():
    '''Parse command line arguments
       --download_ids             Add to the command line to use the bgg APIs
                                  to get game ids
       --download_details         Add to the command line to use the bgg APIs
                                  to use names and ids to retrieve game details
       --send-to-es               Add to the command line to send downloaded
                                  game details to Elasticsearch
       --ids                      Specify a file name for pickled ids structure
       --names                    Specify a file name for pickled names
       --details-file             Specify a file name for game details
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_ids', action='store_true', default=False,
                        help='''Use the API to scan for games first''')
    parser.add_argument('--download_details', action='store_true', default=False,
                        help='''Use the API to download game details''')
    parser.add_argument('--ids', action='store', default='',
                        help='''Source file for pickled ids''')
    parser.add_argument('--names', action='store', default='',
                        help='''Source file for pickled names''')
    parser.add_argument('--details-file', action='store', default='details.txt',
                        help='''Destination file for downloaded game details''')
    parser.add_argument('--send-to-es', action='store_true', default=False,
                        help='''Use the API to download game details''')

    return parser.parse_args()

if __name__ == '__main__':
    '''Main entry. Tries to download or load game names, ids, and details. If
       specified, it sends the details to Elasticsearch. '''
    args = parse_args()
    if not args.download_ids:
        if not args.names or not args.ids:
            err = '''If you're not downloading game ids and names, you must '''
            err += '''specify both a --names file and an --ids file'''
            raise ValueError(err)
    bgg_manager = BGGManager(args.ids, args.names, args.details_file)
    print("Loading game names and ids")
    bgg_manager.load_game_names_and_ids(download=args.download_ids)
    print("Loading details")
    bgg_manager.load_game_details(download=args.download_details)

    esm = ESManager()

    if args.send_to_es:
        print('Deleting games index')
        esm.remove_index('games')
        print('Done')

        mapping = ''
        with open('bgg_mapping.json', 'r') as mapping_file:
            mapping = json.load(mapping_file)

        print('Creating games index')
        esm.create_index('games', json.dumps(mapping))

        print("Sending data")
        for detail in bgg_manager.game_details():
            esm.add_document(detail)
        esm.flush() # Final flush to empty any stragglers.

    print("Done")
