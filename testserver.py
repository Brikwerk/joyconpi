import os
from bluetooth import *
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from dbus.mainloop.glib import DBusGMainLoop

import responses
from btdevice import BTDevice


# Device Info
DEVICE_NAME = "'Joy-Con (L)'"
DEVICE_TYPE = "0x002508" # Gamepad/joystick device class
# Ports
# NOTE: These *must* be the same as the advertised SDP record(s)
# The port in an SDP record should be found in the 0x0004 attribute
# under the UUID 0x0100 as a UINT16 hexadecimal value.
# The alt port can be found in the 0x000d attribute under the same
# UUID (0x0100).
PORT_SDP = 1
PORT_CONTROL = 17
PORT_INTERRUPT = 19
# UUIDs
UUID_SDP = "00001000-0000-1000-8000-00805f9b34fb" # Port 1
UUID_HID = "00001124-0000-1000-8000-00805f9b34fb" # Port 17
UUID_PNP = "00001200-0000-1000-8000-00805f9b34fb"
# Profile Paths
PATH_SDP = "/bluez/brikwerk/joyconpi_SDP"
PATH_HID = "/bluez/brikwerk/joyconpi_HID"
PATH_PNP = ""


if __name__ == '__main__':
    # Check for root
    if not os.geteuid() == 0:
       sys.exit("Please re-run this script as root")
    DBusGMainLoop(set_as_default=True)

    # Initializing device
    device = BTDevice(DEVICE_NAME, DEVICE_TYPE)
    ADDRESS = device.get_address()

    # Adding profiles
    print("")
    print("Configuring BlueZ Profiles...")
    device.add_profile("./sdp/jc_sdp_record.xml", PATH_SDP, UUID_SDP)
    print("Added SDP Profile")
    device.add_profile("./sdp/jc_gamepad_record.xml", PATH_HID, UUID_HID)
    print("HID Profile")

    print("")
    print("Opening to sockets")
    sock_sdp=BluetoothSocket(L2CAP)
    sock_control=BluetoothSocket(L2CAP)
    sock_interrupt=BluetoothSocket(L2CAP)
    print("Binding sockets to address %s" % ADDRESS)
    sock_sdp.bind((ADDRESS, PORT_SDP))
    sock_control.bind((ADDRESS, PORT_CONTROL))
    sock_interrupt.bind((ADDRESS, PORT_INTERRUPT))
    print("Listening on sockets")
    sock_sdp.listen(1)
    sock_control.listen(1)
    sock_interrupt.listen(1)

    try:
        print("")
        print("Advertising UUIDs")
        #advertise_service(sock_sdp, "Service Discovery Server", UUID_SDP)
        #advertise_service(sock_control, "Human Interface Device", UUID_HID)

        print("")
        print("Waiting to accept connections")
        print("")
        client_sdp, sdp_address = sock_sdp.accept()
        print("Got SDP Client Connection")
        client_control, control_address = sock_control.accept()
        print("Got Control Client Connection")
        client_interrupt, interrupt_address = sock_interrupt.accept()
        print("Got Interrupt Client Connection")
        
    except Exception as e:
        print("An Error Occurred:")
        print(str(e))
        print("")

        print("Closing sockets")
        if 'client_sdp' in locals():
            if hasattr(client_sdp, 'close'):
                client_sdp.close()
        sock_sdp.close()

        if 'client_control' in locals():
            if hasattr(client_control, 'close'):
                client_control.close()
        sock_control.close()

        if 'client_interrupt' in locals():
            if hasattr(client_interrupt, 'close'):
                client_interrupt.close()
        sock_interrupt.close()

    client_interrupt.send(responses.REPLY02)
    data = client_interrupt.recv(50)
    print(data)

    Gtk.main()
