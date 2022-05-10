# Project "Pretender"
A Discord bot impersonating users via webhooks, based on their messages, using Markov chains.

Originally created for [r/okbuddyhololive](https://www.reddit.com/r/okbuddyhololive/)'s Discord server, but it can be used for other servers as well.

It uses webhooks to send message to a channel with a custom username and avatar (although, the [BOT] tag is still visible next to the name) & it uses [Markov chains](https://en.wikipedia.org/wiki/Markov_chain) to generate messages.

## Running
Before running the bot, make sure you are running Python 3.8 or later.
You can download the latest version of Python from [Python.org](https://www.python.org/downloads/).

1. Set up a MongoDB database (use the [installation guides](https://www.mongodb.com/docs/manual/administration/install-community/) for help). 
    - You can either install it on your host machine, or use a remote MongoDB server, as long as it's accessible from your
host via a connection URI.
2. Create an application with a bot on [Discord Developer Portal](https://discord.com/developers/applications/).
    - For exact instructions, see [this guide](https://discordpy.readthedocs.io/en/stable/discord.html). It will help you to create an invite link for the bot as well.
3. Clone the repository to your host machine, or download the source code using the `Code > Download ZIP` button.
4. Fill out all the values in the `config.toml` file, according to the comments in the file.
5. Set a permanent system-wide environment variable `DISCORD_TOKEN` with the bot's token, that you can get on the Discord Developer Portal.
    - For Windows, you can use [this](https://www.java.com/en/download/help/path.html) for help.
    - For Linux, you can put `export DISCORD_TOKEN="<BOT_TOKEN_HERE>"` in the file `~/.bashrc` or `~/.zshrc` (depending on your shell).
6. Open a terminal with the bot files in the current directory.
6. Install the dependencies for the bot using `pip`.
    - On Windows, it's: `py -3 -m pip install -r requirements.txt`.
    - On Linux, it's: `python3 -m pip install -r requirements.txt`.
    - You only need to do this once. You can skip this step if you already have the dependencies installed.
7. Run the bot using `python3 main.py` or `py -3 main.py`, depending on your operating system.

## Contributing
If you want to contribute to the project, you can fork the repository on GitHub and make a pull request, if you want to.

We kindly welcome any contributions, even if it's just a simple grammar fix!