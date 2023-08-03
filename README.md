# Farcaster @eatkiwi bot for suggested [Kiwi News](https://news.kiwistand.com) links and titles

Special thanks to @alexpaden for the command framework used here.
Reference: https://github.com/alexpaden/ditti-bot

# Overview

This repository contains the code for the Farcaster @eatkiwi bot, which suggests Kiwi News links and titles. The bot operates using two main components: `stream_notifications` and `stream_casts`.

## Stream Notifications

`stream_notifications` is responsible for listening to incoming notifications on the platform. When a user mentions the bot, the notification is processed, and the bot takes appropriate action based on the mention's content.

### Replies and Mentions

When the bot is mentioned, it checks the content of the mention for a valid command. Currently `eat` is the only valid command, and it is used to suggest a Kiwi News link and title. The default response is the same as the `eat` command, so the bot will respond to any mention or a reply to a cast with a link regardless of the command used.

In the future, additional commands may be added to the bot. For example, a `help` command could be used to display a list of available commands.

The user can specify a style for the title and summary. The default style is `creative, witty and sarcastic` and `in the style of The New Yorker`, but the user can specify a different style by including it in the mention. For example, `@eatkiwi eat in the style of Hacker News <link>` will suggest a title and summary similar to the ones seen on Hacker News.

For convenience, the bot will also respond to any reply to a cast with a link. This allows users to easily suggest a title and summary for a link that has already been casted. For example, a user can reply to a cast that has a link in it with `in the style of Scooby-Doo` and the bot will respond with a title and summary in the style of Scooby-Doo.

## Stream Casts

`stream_casts` is responsible for periodically fetching new content from Kiwi News and broadcasting it to the platform. The bot will post the latest news articles, along with their titles and links, for users to consume.

# Setup

## Development

Run a local MongoDB instance to store links that are casted. This is used to prevent duplicate casts from being posted.
`docker run -d -p 27017:27017 --name my-mongo mongo:latest`

Use `pytest` to run tests. e.g. `pytest --log-cli-level=DEBUG tests/test_reply.py`

# Testing

Example: `pytest --log-cli-level=INFO tests/test_get_thread.py`
