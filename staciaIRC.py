import os, sys, random, requests
from bs4 import BeautifulSoup
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import sys
import queryparser


class StaciaBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, question, classifier, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.question = question
        self.classifier = classifier

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection
        if cmd == "bye":
            self.disconnect()
        elif cmd == "bye":
            self.die()
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        elif cmd == "hello":
            c.privmsg(self.channel, "Hi! Ask me a question!")
        elif cmd == "about":
            c.privmsg(self.channel, "Welcome to the StaCIA Bot to help with your questions on tutoring and clubs for both CSSE and STAT in Cal Poly!")
        elif cmd == "usage":
            c.privmsg(self.channel, "Enter your question and I'll be happy to provide you an answer! Just tell me bye when you're done!")
        else:
            parsedQuery = queryparser.parseQuery(cmd, self.question, self.classifier)
            # response = getanswer(parsedQuery)
            # print(response)
def main():
    if len(sys.argv) != 4:
        print("Usage: StaciaBot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]
    question, variable = queryparser.parseQuestions()
    classifier = queryparser.createModel(question)
    bot = StaciaBot(channel, question, classifier, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()