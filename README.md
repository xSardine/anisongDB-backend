# AnisongDB - Back-End

TODO list before using this in production

> - Implement support for Back-ups
> - Artist with multiple role in same line_up
> - sort results
> - reverse line ups order so that it goes 0 = oldest, 1 = second oldest, etc... & automatically assign newest to new songs
> - Document Regex better
> - Document the fact that db is not being updated on this git regularly
> - Document the consequences of attributes not updated regularly better
> - Mentions front-end in the readme
> - Search artist name directly if no ID found
> - Finish implementing current search parameters for each end points
> - Add case sensitive & exact match search possibilities
> - Use max number of songs earlier in the search to optimize edge cases
> - Rework the front-end with the new API
> - Implement the new front-end and back-end in a development server, and let people who have been using the old version test it and adapt their code to the new API

This repository contains the future back-end of [AnisongDB](https://anisongdb.com/).  
Built with [FastAPI](https://fastapi.tiangolo.com/)

## Features

This database is being built upon the AMQ Database. Its main goal is to provide a more complete database for the AMQ community : artists relations, groups, composers, arrangers, etc...

The search functions will see their functionalities limited during AMQ Ranked Time to prevent cheating.  
Here are the hours during which the search functions will be limited:

- 20:30 - 21:28 CST
- 20:30 - 21:28 JST
- 20:30 - 21:28 CET

## Stability

This a `work in progress`, and the API is not in its final state.  
Be aware that even though I will try to keep incompatibilies between versions at a minimum, the API is subject to change.

The database is updated pretty much daily through AMQ's Expand Database.
This also means that any info that is not available in Expand Database will not be updated regularly.  

This includes :

- Anime type, season, alternative names, genres, tags and animelist website IDs (MAL, AniList, etc...)
- Song difficulty and category

Last update for these was on 2023-04-13.

## Contributing

If you wish to contribute, please read the following [recommendations](/CONTRIBUTING.md).

## Architecture

The FastAPI application is in the directory `app`.  
The directory `app/data` contains the database. It is not the one being used in production, as I don't want to expose it publicly. Instead it is a copy of the database, with some data removed, such as catbox links to the song's video.

The directory `misc_scripts` contains a collection of scripts that I used to process the data, and maintain the database. There are some more scripts that I use but have yet to publish as they are too ugly to be seen by the public. Locally, I maintain the database using `.json` files, as I can easily access them and modify them when I encounter exceptions that I have not automated yet. I then use the scripts in `process_data_scripts/convert_to_SQL.py` to convert the `.json` files to the sqlite format for productions use. No continuous deployment yet, I send the database to my server and then restart the server manually.

## Installation

[Installation guide](/INSTALL.md)

## Licence

The code is licensed under the [GPLv3](/LICENSE) licence. As a copyleft licence, it essentially ensures that any derivative work is also licensed under the same terms.  
However it does not apply to the data, for which I don't have the full rights as I am merely building upond an existing work which is technically not published.

## Special Thanks

Special thanks to :

- Egerod for developing [AMQ](https://animemusicquiz.com/), and for "providing" the database that I am building upon.
- AMQ mods for their intensive work of the database.
- The AMQ community for their help in maintaining the database.
- The contributors of the [previous version of the repository](https://github.com/xSardine/AMQ-Artists-DB) who helped reporting bugs and suggesting improvements.
- [MugiBot](https://github.com/CarrC2021/MugiBot) for providing me their database, which helped me on the first iteration.
