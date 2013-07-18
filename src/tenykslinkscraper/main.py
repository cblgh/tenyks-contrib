import requests
import re
import logging
from tenyksclient.client import Client, run_client, settings


class TenyksLinkScraper(Client):

    direct_only = False
    irc_message_filters = {
        'link_posted': [r'\(?\b(http|https)://[-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]'],
    }

    # MONKEYPATCHING IS DUMB
    def __init__(self, name):
            self.channels = [settings.BROADCAST_TO_CLIENTS_CHANNEL]
            self.name = name.lower().replace(' ', '')
            if self.irc_message_filters:
                self.re_irc_message_filters = {}
                for name, regexes in self.irc_message_filters.iteritems():
                    if not name in self.re_irc_message_filters:
                        self.re_irc_message_filters[name] = []
                    if isinstance(regexes, basestring):
                        regexes = [regexes]
                    for regex in regexes:
                        self.re_irc_message_filters[name].append(
                            re.compile(regex).search)
            if hasattr(self, 'recurring'):
                gevent.spawn(self.run_recurring)
            self.logger = logging.getLogger(self.name)

    def handle_link_posted(self, data, match):
        if settings.POST_URL is None:
            self.logger.debug('No POST_URL in the settings for this service. Cannot post.')
            return None

        url = match.group()
        payload = '{"url": "%s", "person": "%s"}' % (match.groups(0)[0], data['nick'])

        req = requests.post(settings.POST_URL,
            data=payload,
            headers={'content-type': 'application/json'})

        self.logger.debug('Posted {url} to {post_url}. Response code was {code}'.format(
            code=unicode(req.status_code),
            url=url,
            post_url=settings.POST_URL))

def main():
    run_client(TenyksLinkScraper)

if __name__ == '__main__':
    main()