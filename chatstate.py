# coding=utf-8
from __future__ import print_function

import departures
from keys import hsl_username, hsl_passcode
from transitions import Machine
import json

fake_location = (60.171944, 24.941389)


class Message(object):
    def __init__(self, text, choices):
        self.text = text
        self.choices = choices


class ChatState(object):
    states = ["initial", "select language", "waiting", "stop departures",
              "list stops",
              "setting city",
              "setting stop", "list"]

    def __init__(self, user):
        self.user = user
        self.settings = {}
        self.current_message = ""
        self.hsl = departures.HslRequests(hsl_username,
                                          hsl_passcode)

        # self.loadstate()
        self.machine = Machine(model=self, states=ChatState.states,
                               initial="initial")
        self.machine.add_transition(trigger="wake_up", source="initial",
                                    dest="select language", after="welcome")
        self.machine.add_transition(trigger="language_selected",
                                    source="select language",
                                    dest="waiting",
                                    after="save_setting")
        self.machine.add_transition(trigger="stop requested", source="waiting",
                                    dest="stop departures")

    def get_waiting_message(self):
        return Message("", choices={"location": "loc",
                                    "departures for a stop": "stop"})

    def get_message(self):
        return self.current_message

    def handle_input(self, message):
        if self.state == "select language":
            self.language_selected("language", message)
        else:
            self.list_stop(message)

    def save_setting(self, name, value):
        self.settings["name"] = value

    def welcome(self):
        text = "Welcome, Tervetuloa! What language do you prefer? Mitä kieltä haluat käyttää?"
        choices = {"English": "en", "suomi": "fi"}
        self.current_message = Message(text, choices)

    def list_stop(self, message):
        return Message(self, choices={"More departures": "more"})


if __name__ == '__main__':
    cs = ChatState("timo")
    cs.wake_up()
    s = ""
    while s != "quit":
        print(cs.get_message().text)
        print(cs.get_message().choices)
        s = raw_input(">>> ")

        # print(hsl.stops_for_location(fake_location[0], fake_location[1]))
