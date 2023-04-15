# AnisongDB - Back-End

This repository contains the back-end of [Anisongdb](https://anisongdb.com/).  
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

- Anime type, vintage, alternative names, genres, tags and animelist website IDs (MAL, AniList, etc...)
- Song difficulty and category

Last update for these was on 2023-04-13.

## Contributing

If you wish to contribute, please read the following [recommendations](/CONTRIBUTING.md).

## Architecture

The FastAPI application is in the directory `app`.  
The directory `app/data` contains the database. It is not the one being used in production, as I don't want to expose it publicly. Instead it is a copy of the database, with some data removed, such as catbox links to the song's video.

The directory `process_data_scripts` contains a collection of scripts that I used to process the data, and maintain the database. There are some more scripts that I use but have yet to publish as they are too ugly to be seen by the public. Locally, I maintain the database using `.json` files, as I can easily access them and modify them when I encounter exceptions that I have yet to automate. I then use the scripts in `process_data_scripts/convert_to_SQL.py` to convert the `.json` files to the sqlite format for productions use.

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
