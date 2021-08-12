#Universidad del Valle de Guatemala
#Redes
#Oliver Graf - 17190

#Load packages used
import logging
import asyncio
from getpass import getpass
from argparse import ArgumentParser

import slixmpp

from slixmpp.exceptions import IqError, IqTimeout

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class register_client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler('register', self.create_account)
        self.add_event_handler('disconnected', self.disconnected)
        self.register_plugin('xep_0077')

    def diconnected(self, event):
        print('The client was disconnected. Rerun program to try again.')

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

        self.disconnect()


# Client class where we define the behavior of the xmpp Client
class my_client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, nick):

        #ClientXMPP inherited init
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.nick = nick

        #We add event handlers for the different functionalities.
        #When a stanza is recieved, these event handlers are triggered
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('disconnected', self.disconnected)
        self.add_event_handler('failed_auth', self.login_fail)
        self.add_event_handler('error', self.handle_error)
        self.add_event_handler("message", self.message_recieved)
        self.add_event_handler('presence_subscribed', self.new_subscriber)

        self.register_plugin('xep_0078')

        #We register plugin xep_0077 to facilitate registration
        self.register_plugin('xep_0077')

        #We register plugin xep_0045 to enable joining muc room
        self.register_plugin('xep_0045')


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

    async def message_recieved(self, msg):
        if msg['mucnick'] != self.nick:
            if msg['type'] == 'error':
                print('Error message from server >> '+msg['body'])
            elif msg['type'] in ('normal', 'chat'):
                print('Direct message from '+ str(msg['mucnick'])+ ': '+msg['body'])
            elif msg['type'] == 'groupchat':
                print('Group message from '+ str(msg['mucnick'])+ ': '+msg['body'])
        else:
            pass

    async def send_direct(self, to):
        msg = input('Type direct message > ')
        self.send_message(mto = to, mbody = msg, mtype = 'chat', mnick = self.nick)


    async def send_group(self, to):
        msg = input('Type group message > ')
        self.send_message(mto = to, mbody = msg, mtype = 'groupchat', mnick = self.nick)


    def handle_error(self):
        print("An error occured, try again\n")
        self.disconnect()

    def login_fail(self):
        print("The login was unsuccsessful, try again\n")
        self.disconnect()


    def diconnected(self, event):
        print('The client was disconnected. Rerun program to try again.')

    async def delete_account(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.full
        resp['register']['remove'] = True

        try:
            resp.send()
            print('Your account has been eliminated succesfully\n')
            self.disconnect()
        except IqError as err:
            print('An error occured while trying to delete your account, try again\n')
            self.disconnect()
        except IqTimeout:
            print('Server response timed out, try again\n')
            self.disconnect()

    def subscribe(self, user):
        self.send_presence_subscription(pto=user, ptype='subscribe', pfrom = self.boundjid.bare)
        self.get_roster()


    def new_subscriber(self, presence):
        print(presence.get_from().bare +' subscribed to you.\n')


# Main function and others

def menu1():
    print('''======== Welcome to the Client ========
    1. Log in
    2. Create account
    3. Close programm''')

def menu2():
    print(''' ==== You are logged in ====
    1. Send direct messages
    2. Send groupchat messages
    3. Add user to contact list
    4. Show contact details
    5. Delete account and exit
    6. Exit
    ''')

async def main_menu(xmpp):
    running = True
    while(running):
        menu2()
        opt = int(input('Select an option number> \n'))
        if opt == 1:
            user = input('Type user JID to message> \n')
            xmpp.send_direct(user)

        elif opt == 2:
            user = input('Type user JID to message> \n')
            xmpp.send_group(user)
        elif opt == 3:
            user = input('Type user JID to add> \n')
            xmpp.subscribe(user)
        elif opt == 4:
            pass
        elif opt == 5:

            xmpp.delete_account()
            running = False
        elif opt == 6:

            running = False

            exit()
        else:
            print('\nInvalid option, try again\n')

async def connect_process(xmpp):
    xmpp.connect()
    xmpp.process()


runner = True
while(runner):
    menu1()
    opti = int(input('Select an option number> \n'))
    if opti == 1:
        try:
            user = input('Type in username> \n')
            password = input('\nType in password> \n')
            nick = input('\nType in nickname> \n')
            xmpp = my_client(user, password, nick)
            print('Instancia creada')
            xmpp.connect()
            #xmpp.loop.run_until_complete(xmpp.connected_event.wait())
            xmpp.loop.create_task(main_menu(xmpp))
            xmpp.process(forever=False)
        except Exception as e:
            print("Error:", e)


    elif opti == 2:
        print('\n Input new account username and password> \n')
        username = input('Username: \n')
        password = input('Password: \n')
        try:
            xmpp = register_client(jid=username, password=password)
            xmpp.register_plugin('xep_0030')  # Service Discovery
            xmpp.register_plugin('xep_0004')  # Data forms
            xmpp.register_plugin('xep_0066')  # Out-of-band Data
            xmpp.register_plugin('xep_0077')  # In-band Registration
            xmpp.register_plugin('xep_0045')  # Groupchat
            xmpp.register_plugin('xep_0199')  # XMPP Ping
            xmpp['xep_0077'].force_registration = True

            xmpp.connect()
            xmpp.process(forever=False)
        except Exception as e:
            print("Error:", e)

    elif opti == 3:
        print('Buhbye!')
        runner = False
    else:
        print('\nInvalid option, try again\n')
