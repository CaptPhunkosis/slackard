# slackard

A Slack bot (slack.com)

Slackard listens to the configured channel and is capable of responding to
message events occurring in that channel.

## Configuration

See the included slackard.yaml configuration file for supported options.
All are required except boticon and botemoji, which are both optional. If
both are provided then botemoji will override boticon (per the Slack API).

## Plugins

A basic plugin system enables you to add whatever functionality you need to
your bot. You may wish for it to respond to particular commands, or to
listen for certain words, or even watch the entire channel conversation.

Slackard provides decorators supporting 3 types of registration to suit your
need. In all cases the only messages passed will be those not produced by
the bot itself. This is to avoid getting stuck in message read-respond loops.

Examples are included in the plugins directory.

### Command

This provider allows you to process specific commands directed at the bot by
name. eg. If the configuration set a botnick of 'slack', then
'slack: say Hello world' would pass 'Hello world' to anything that has
subscribed to the command 'say'.

```python
@bot.command('say')
def command_say(args):
    bot.speak('You asked me to say, "{0}"'.format(args))
```

### Subscribe

The plugin subscribes to a particular pattern. This is any pattern that can
be passed through re.compile, and is applied to each message received by the
bot. If a message matches then the entire message is passed.

```python
@bot.subscribe('cookie')
def sub_cookie(message):
    bot.speak('I see a cookie in "{0}"'.format(message))
```

### Firehose

The plugin receives a full feed of channel traffic.

```python
@bot.firehose
def listen(message):
    # Do something with `message`
    pass
```
