> As of March 16, 2024, linaSTK (at least, for the original Revolt version) has been discontinued. The [Discord version](https://codeberg.org/linaSTK/bot) (hosted on Codeberg) will continue to be worked on.

<img align='right' width=25% height=25% src='https://autumn.revolt.chat/avatars/5YHRpsn89R4NK0P--iq_FFRCOiMZ1M8fGJWN0kmrJh/Untitled4_20231004182737.png'/>

# lina
A [Revolt](https://github.com/revoltchat) bot focused on SuperTuxKart, based on the code from [doingus](https://github.com/searinminecraft/doingus).

## Features

* Search for servers
* Get currently online servers (aka if server has players in it)
* Search for users (Max results is 50. It's a limitaion on STK servers)
* Allows for setting up a channel to display list of online players (Must be done manually for now)
* Get addon information (only tracks for now)
* A game that makes you guess what addon it is based on the image it gives you
* Get player rankings (Only top 10 players for now)
* "PokeMap" system: A Pokemon-like mechanic where you "catch" and collect addons
* Query when the user was last online or detected (Inspired by NobWow's stk-seen command) (fully Implemented on rewrite)
* Get a player's friends list (Only using User IDs for now)

## How to set up

(WIP)

## Plans for the bot

* Easy configuration though a configuration file or server commands
* Opening the bot to the general public (a.k.a it can invited to groups, servers, etc.)
* Caching player names (so that people can type the username instead of the user ID. It works by taking the usernames from various sources such as user search results and online players)
* ~~Player tracking (a feature that was widely used the SuperTuxKart Discord Server to allow for tracking player activity via DMs. It used the [Snakebot](https://github.com/NobWow/snakebot) Discord bot via an [extension](https://gist.github.com/NobWow/6578943f77d7d7cbf3b227877a480860))~~ (Implemented in rewrite)

# Disclaimer

This bot relies on a SuperTuxKart account that is always online to retrieve data from API endpoints that require authentication (such as friends lists, rankings, user info, etc.). It is a violation of the SuperTuxKart Terms of Service and could result in your IP possibly being blocked. While we combat these issues by polling SuperTuxKart servers every few minutes (which is normal behavior in the game) and spoofing the user agent to `SuperTuxKart/1.4 (Linux)`, there is no gurantee that it will protect the bot from it. So you use this bot at your own risk.

# Credits

* [NobWow](https://github.com/NobWow) - For generously hosting this bot and all of my other bots ~~on his spare laptop~~. For helping me with the code and mostly SQL stuff. Without him then this bot wouldn't have used databases for things like PokeMap.
* ~~[kimden](https://github.com/kimden)~~ - ~~For hating on Revolt and the bot~~
