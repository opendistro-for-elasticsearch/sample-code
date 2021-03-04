# BGG - Download and search board game data from BoardgameGeek.com

This sample application uses the boardgamegeek2 library (available on PyPi) to 
download names, ids, and full descriptions for board games from 
boardgamegeek.com's API. It uses the es_sink library to send the board game 
details to an Open Distro for Elasticsearch cluster running on localhost. Of 
course, you can change that and send it to any Elasticsearch cluster.

# Prerequisite

This example uses the es_sink library, provided in this repo. To install,

```
> pip install <path_to_community_repo>/es_sink
```


# Usage

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
