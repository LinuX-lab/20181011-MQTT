#!/usr/bin/python3
# coding=utf-8

"""
Prosty komunikator na MQTT
"""

import argparse
import tkinter as tk

import paho.mqtt.client as mqtt


class Application(tk.Frame):
    def __init__(self, args, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.username = args.username
        self.client = mqtt.Client(userdata=self)

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(args.server, args.port)
        self.client.loop_start()

    def createWidgets(self):
        self.display_text = tk.StringVar()
        self.msgOut = tk.Label(self, height=10, width=40, textvariable=self.display_text, anchor=tk.NW, justify=tk.LEFT)
        self.msgOut.grid()

        self.msgIn = tk.Entry(self, width=40)
        self.msgIn.grid()
        self.msgIn.bind('<Return>', self.on_enter_key)

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid()

    def on_enter_key(self, _event):
        m = self.msgIn.get()
        if m.startswith("/"):
            [hd, tl] = m.split(" ", maxsplit=1)
            user = hd.strip('/')
            self.client.publish("messages/" + user, tl)

        else:
            self.client.publish("messages/_", m)
        self.msgIn.delete(0, len(m))


def on_connect(client, userdata, _flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("messages/_")  # Broadcast
    client.subscribe(f"messages/{userdata.username}")  # Unicast


def on_message(_client, userdata, msg):
    oldmsg = userdata.display_text.get()
    userdata.display_text.set(oldmsg + "\n" + msg.payload.decode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port of MQTT broker", type=int, default=1883)
    parser.add_argument("-s", "--server", help="Address MQTT broker", default="127.0.0.1")
    parser.add_argument("username", help="User name")
    args = parser.parse_args()

    app = Application(args)
    app.master.title('Messenger: ' + args.username)
    app.mainloop()
