# rally-decode

Reverse-engineering leaderboard data from old PC rally games.

## What?

Converts binary encoded save data into a human-readable format.

Turns 

```
3440   4d 43 52 41 45 00 05 00 00 00 00 00 50 53 00 49    MCRAE       PS I
3456   4e 20 4d 43 52 41 45 00 43 b0 81 2a 43 4f 4c 49    N MCRAE C  *COLI
3472   4e 20 4d 43 52 41 45 00 dd da 01 00 43 4f 4c 49    N MCRAE     COLI
3488   4e 20 4d 43 52 41 45 00 ff e9 01 00 43 4f 4c 49    N MCRAE     COLI
```

Into
```
  New Zealand 1           PS 18:26.59 Subaru Impreza WRC A
  New Zealand 2  COLIN MCRAE 20:15.65 Subaru Impreza WRC A
  New Zealand 3  COLIN MCRAE 20:54.39 Subaru Impreza WRC A
```

## Why?

Many games remain fun to play and compete on, but date from a time before online functionality was commonplace. This project aims to breathe some new life into some of my favorites. 

## Usage

#### `python3 configure.py` 

Prompts you to set the required environment variables.

#### `python3 upload.py` 

Automatically decodes and uploads records to an [online leaderboard](https://github.com/psaikko/rally-leaderboard).

#### `python3 -m cmr.decode <path to cmRally.cfg>` 

Reads Colin McRae Rally configuration file and outputs leaderboard times in plain text.

#### `python3 -m cmr2.decode <path to GameInfo.rcf>` 

Reads Colin McRae Rally 2.0 configuration file and outputs leaderboard times in plain text.

## Games supported

- [Colin McRae Rally](https://www.pcgamingwiki.com/wiki/Colin_McRae_Rally)

- [Colin McRae Rally 2.0](https://www.pcgamingwiki.com/wiki/Colin_McRae_Rally_2.0)