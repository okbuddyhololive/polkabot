# polkabot's Privacy Policy

## Introduction
polkabot is a Discord bot, for impersonating users based on their messages they have sent to a server.
Because of this, we are required to process data about the users' messages. This Privacy Policy describes how we collect and use that data. Any mentions of "we", "our", "us" refer to the developers of the bot ("DocileSphinx" and "bemxio"). "They", "them", "their" refer to the users of the bot.

## Data Collection and Usage
We are collecting data about messages sent by members in the server. The data later on is used to generate a message that will be sent to the user invoking the bot.
As such, we are not storing any personal data about the users, except for their Discord ID, which is used to identify them for gathering messages for impersonation.

The exact data that is taken is as follows:
- A user's Discord ID, used to gathering all of their messages that the bot collected.
- The message content they sent, which is used to generate the message that will be sent to the bot invoker.

The message data is stored in a database, and is not shared with anyone else, except for us and the bot.

## User Rights
Users have the full right to opt out of the data collection process. To do so, they can use the `$optout` command, which will remove their data from the database, as well as add them to the blacklist, that will prevent their messages from being stored.

If any issues with the opting-out process occur, please contact us directly via Discord.