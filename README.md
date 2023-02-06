# Mastodon Hourly Pics Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A Mastodon bot written in Python that sends random images every hour.

### Features

- Posts single images only
- Supports JPEG, PNG, WebP, and GIF images
- No restart required after adding/removing/renaming images
- Posts at a specific minute of the hour (at the top of the hour by default)
- Prevents pics from being posted at least twice in a row by default
- Random delay of up to 30 seconds before sending a new image

### Setup

0. If you don't have a bot account and/or application set up, follow [this guide](https://botwiki.org/resource/tutorial/how-to-make-a-mastodon-botsin-space-app-bot/) first. (They used botsin.space as an example, this applies to any Mastodon instance.)

1. Install dependencies by running `pip install -r requirements.txt`

2. Copy `settings.example.yaml` and `secrets.example.yaml` to `settings.yaml` and `secrets.yaml` respectively in the same directory

3. Paste your app credentials into `secrets.yaml`

4. Set up the URL of your bot's Mastodon instance and the path to the images directory in `settings.yaml`

### Usage

Start the bot with `python -m mstdnhourlypics`. Make sure your current working directory is the project root (meaning the directory where this readme is found) when you run this command.

To exit out of the bot, just press <kbd>Ctrl</kbd>+<kbd>C</kbd> or send a [SIGINT](https://en.wikipedia.org/wiki/SIGINT_(POSIX)) signal to the bot process.

---

Copyright 2023 [@p1timmy](https://neso.page/@p1timmy). Some rights reserved, released under the MIT License.
