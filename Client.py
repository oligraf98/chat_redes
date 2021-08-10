#Universidad del Valle de Guatemala
#Redes
#Oliver Graf - 17190

#Load packages used
import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp

from slixmpp.exceptions import IqError, IqTimeout

# Client class where we define the behavior of the xmpp Client
class my_client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):

        #ClientXMPP inherited init
        slixmpp.ClientXMPP.__init__(self, jid, password)

        #We add event handlers for the different functionalities.
        #When a stanza is recieved, these event handlers are triggered
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('register', self.create_account)
        self.add_event_handler('disconnected', self.disconnected)
        self.add_event_handler('failed_auth', self.login_fail)
        self.add_event_handler('error', self.handle_error)
        self.add_event_handler("message", self.message)

        #We register plugin xep_0077 to facilitate registration
        self.register_plugin('xep_0077')

        self['xep_0077'].force_registration = True

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()


    def create_account(self, event):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send()
            print('Your account has been created\n')
        except IqError:
            print('An error occured while trying to create your account, try again\n')
        except IqTimeout:
            print('Server response timed out, try again\n')

    def handle_error(self):
        print("An error occured, try again\n")
        self.disconnect()

    def login_fail(self):
        print("The login was unsuccsessful, try again\n")
        self.disconnect()

    def start(self):
        self.send_presence()
        self.get_roster()

    def diconnected(self, event):
        print('The client was disconnected. Rerun program to try again.')

    def delete_account(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.full
        resp['register']['remove'] = True

        try:
            resp.send()
            print('Your account has been eliminated succesfully\n')
        except IqError as err:
            print('An error occured while trying to delete your account, try again\n')
            self.disconnect()
        except IqTimeout:
            print('Server response timed out, try again\n')
            self.disconnect()
