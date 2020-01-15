"""
JoyConPi - A JoyCon Emulator for Raspberry Pi

Copyright (C) 2020-2020  Reece Walsh <reece@brikwerk.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 and
only version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

"""

import os
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib


class BTDevice():

    ADDRESS = None
    DEVICE_NAME = None
    DEVICE_TYPE = None

    def __init__(self, device_name, device_type):
        """Creates a Bluetooth device
        :param device_name: The friendly name of the BT device as a string
        :param device_type: The device type code as a string
        """

        print("")
        print("Getting/checking BT address...")
        self.ADDRESS = os.popen("hciconfig hcio | awk '/BD Address: /{print $3}'").read().strip()
        if type(self.ADDRESS) != str:
            raise ValueError("Expected Address of type string, got %s" % str(type(self.ADDRESS)))
        elif len(self.ADDRESS) != 17:
            raise ValueError("BT Address improper length. Got %s, expected 17." % len(self.ADDRESS))
        elif not ":" in self.ADDRESS:
            raise ValueError("Improper BT Address formatting. No colons detected.")
        print("Address: %s" % self.ADDRESS)

        print("")
        self.DEVICE_TYPE = device_type
        self.DEVICE_NAME = device_name
        print("Setting up BT Adapter...")
        os.popen("hciconfig hcio class %s" % self.DEVICE_TYPE)
        print("Device class set to %s" % self.DEVICE_TYPE)
        os.popen("hciconfig hcio name %s" % self.DEVICE_NAME)
        print("Device name set to %s" % self.DEVICE_NAME)
        os.popen("hciconfig hcio piscan")
        print("Device is now discoverable")

    def add_profile(self, sdp_record_path, profile_path, uuid):
        """Adds a profile to the bluetooth device
        :param sdp_record_path: The path to the XML sdp record as a string
        :param profile_path: The path of the profile as a string
        :param uuid: The UUID of the profile as a string
        """

        sdp_record = self.load_sdp_record(sdp_record_path)
        opts = {
            "ServiceRecord":sdp_record,
            "Role":"pnp-server",
            "RequireAuthentication":False,
            "RequireAuthorization":False
        }

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez","/org/bluez"), "org.bluez.ProfileManager1")

        profile = BTProfile(bus, profile_path)
        print(uuid)
        manager.RegisterProfile(profile_path, uuid, opts)

    def load_sdp_record(self, path):
        record = None
        try:
            with open(path, "r") as f:
                record = f.read()
        except e:
            raise OSError("Could not load the SDP record: %s" % str(e))
        return record

    def get_address(self):
        return self.ADDRESS


##############################
# Start BlueZ Code
##############################
# The below code is from:
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/test-profile

"""

	BlueZ - Bluetooth protocol stack for Linux

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License version 2 and
	only version 2 as published by the Free Software Foundation.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

"""

class BTProfile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.fd > 0):
            os.close(self.fd)
            self.fd = -1

    def __init__(self, manager, path):
        dbus.service.Object.__init__(self, manager, path)

##############################
# End BlueZ Code
##############################
