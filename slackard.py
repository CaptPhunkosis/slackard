#!/usr/bin/env python

from __future__ import print_function

import functools
import re
import slacker
import sys
import time
import yaml


class SlackardFatalError(Exception):
    pass


class SlackardNonFatalError(Exception):
    pass


class Config(object):
    config = {}

    def __init__(self, file_):
        f = open(file_, 'r')
        y = yaml.load(f)
        f.close()
        self.__dict__.update(y)


class Slackard(object):

    subscribers = []
    commands = []
    firehoses = []

    def __init__(self, config_file):
        self.config = Config(config_file)
        self.apikey = self.config.slackard['apikey']
        self.botname = self.config.slackard['botname']
        self.botnick = self.config.slackard['botnick']
        self.channel = self.config.slackard['channel']
        try:
            self.boticon = self.config.slackard['boticon']
        except:
            self.boticon = None
        try:
            self.botemoji = ':{0}:'.format(self.config.slackard['botemoji'])
        except:
            self.botemoji = None

    def __str__(self):
        return 'I am a Slackard!'

    def _import_plugins(self):
        import plugins
        plugins.init_plugins(self)

    def _init_connection(self):
        self.slack = slacker.Slacker(self.apikey)
        try:
            r = self.slack.channels.list()
        except slacker.Error as e:
            if e.message == 'invalid_auth':
                raise SlackardFatalError('Invalid API key')
            raise
        except Exception as e:
            raise SlackardNonFatalError(e.message)

        c_map = {c['name']: c['id'] for c in r.body['channels']}
        self.chan_id = c_map[self.channel]

    def _fetch_messages_since(self, oldest=None):
        h = self.slack.channels.history(self.chan_id, oldest=oldest)
        assert(h.successful)
        messages = h.body['messages']
        messages.reverse()
        return [m for m in messages if m['ts'] != oldest]

    def speak(self, message, paste=False):
        if paste:
            message = '```{0}```'.format(message)
        self.slack.chat.post_message(self.chan_id, message,
                                     username=self.botname,
                                     icon_emoji=self.botemoji,
                                     icon_url=self.boticon)

    def upload(self, file, filename=None, title=None):
        channels = self.chan_id
        if title is None:
            title = ''
        title = '{} (Upload by {})'.format(title, self.botname)
        self.slack.files.upload(file, channels=channels,
                                filename=filename,
                                title=title)

    def run(self):
        self._init_connection()
        self._import_plugins()

        cmd_matcher = re.compile('^{0}:\s*(\S+)\s*(.*)'.format(
                                 self.botnick), re.IGNORECASE)
        h = self.slack.channels.history(self.chan_id, count=1)
        assert(h.successful)
        ts = h.body['messages'][0]['ts']
        t0 = time.time()

        while True:
            t1 = time.time()
            delta_t = t1 - t0
            if delta_t < 5.0:
                time.sleep(5.0 - delta_t)
            t0 = time.time()

            try:
                messages = self._fetch_messages_since(ts)
            except Exception as e:
                # Possibly an error we can recover from so raise
                # a non-fatal exception and attempt to recover
                raise SlackardNonFatalError(e.message)

            for message in messages:
                ts = message['ts']
                if 'text' in message:
                    # Skip actions on self-produced messages.
                    try:
                        if (message['subtype'] == 'bot_message' and
                                message['username'] == self.botname):
                            continue
                    except KeyError:
                        pass
                    print(message['text'])
                    for f in self.firehoses:
                        f(message['text'])
                    for (f, matcher) in self.subscribers:
                        if matcher.search(message['text']):
                            f(message['text'])
                    m = cmd_matcher.match(message['text'])
                    if m:
                        cmd, args = m.groups()
                        for (f, command) in self.commands:
                            if command == cmd:
                                f(args)

    def subscribe(self, pattern):
        if hasattr(pattern, '__call__'):
            raise TypeError('Must supply pattern string')

        def real_subscribe(wrapped):
            @functools.wraps(wrapped)
            def _f(*args, **kwargs):
                return wrapped(*args, **kwargs)

            try:
                matcher = re.compile(pattern, re.IGNORECASE)
                self.subscribers.append((_f, matcher))
            except:
                print('Failed to compile matcher for {0}'.format(wrapped))
            return _f

        return real_subscribe

    def command(self, command):
        if hasattr(command, '__call__'):
            raise TypeError('Must supply command string')

        def real_command(wrapped):
            @functools.wraps(wrapped)
            def _f(*args, **kwargs):
                return wrapped(*args, **kwargs)

            self.commands.append((_f, command))
            return _f

        return real_command

    def firehose(self, wrapped):
        @functools.wraps(wrapped)
        def _f(*args, **kwargs):
            return wrapped(*args, **kwargs)

        self.firehoses.append(_f)
        return _f


def main():
    bot = Slackard('slackard.yaml')
    while True:
        try:
            bot.run()
        except SlackardFatalError as e:
            print('Fatal error: {}'.format(e.message))
            sys.exit(1)
        except SlackNonFatalError as e:
            print('Non-fatal error: {}'.format(e.message))
            delay = 5
            print('Delaying for {} seconds...'.format(delay))
            time.sleep(delay)
            bot._init_connection()
        except Exception as e:
            print('Unhandled exception: {}'.format(e.message))
            sys.exit(1)


if __name__ == '__main__':
    main()
