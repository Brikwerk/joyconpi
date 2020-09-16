import asyncio, socket, sys, os, subprocess, time, fcntl

from bluez import BlueZ
from hid import HIDGamepad
import responses as resp
from utils import print_msg_controller, print_msg_switch


jc_MAC = "60:6B:Ff:D9:E2:2D"
port_ctrl = 17
port_itr = 19

bt = BlueZ()
bt.toggle_input_plugin(False)

controller = HIDGamepad(bt, "Joy-Con (L)", "./sdp/switch-controller.xml")

# Joy-Con Sockets
jc_ctrl = socket.socket(family=socket.AF_BLUETOOTH,
                        type=socket.SOCK_SEQPACKET,
                        proto=socket.BTPROTO_L2CAP)
jc_itr = socket.socket(family=socket.AF_BLUETOOTH,
                        type=socket.SOCK_SEQPACKET,
                        proto=socket.BTPROTO_L2CAP)

# Switch sockets
switch_itr = socket.socket(family=socket.AF_BLUETOOTH,
                            type=socket.SOCK_SEQPACKET,
                            proto=socket.BTPROTO_L2CAP)
switch_ctrl = socket.socket(family=socket.AF_BLUETOOTH,
                            type=socket.SOCK_SEQPACKET,
                            proto=socket.BTPROTO_L2CAP)

try:
    bt.set_alias("Nintendo Switch")
    print("Connecting to Joy-Con: ", jc_MAC)
    jc_ctrl.connect((jc_MAC, port_ctrl))
    jc_itr.connect((jc_MAC, port_itr))
    print("Got connection.")

    switch_ctrl.bind((bt.address, port_ctrl))
    switch_itr.bind((bt.address, port_itr))

    bt.set_alias("Joy-Con (L)")
    bt.set_discoverable(True)

    print("Waiting for Switch to connect...")
    switch_itr.listen(1)
    switch_ctrl.listen(1)
    
    client_control, control_address = switch_ctrl.accept()
    print("Got Switch Control Client Connection")
    client_interrupt, interrupt_address = switch_itr.accept()
    print("Got Switch Interrupt Client Connection")

    # Creating a non-blocking client interrupt connection
    fcntl.fcntl(client_interrupt, fcntl.F_SETFL, os.O_NONBLOCK)

    # Initial Input report from Joy-Con
    jc_data = jc_itr.recv(50)
    print("Got initial Joy-Con Empty Report")
    print_msg_controller(jc_data)

    # Send the input report to the Switch a couple times
    for i in range(5):
        print("Sending input report", i)
        client_interrupt.sendall(jc_data)
        time.sleep(1)
    
    # Get the Switch's reply and send it to the Joy-Con
    reply = client_interrupt.recv(50)
    print_msg_switch(reply)
    jc_itr.sendall(reply)

    # Sending Switch the proxy's device info
    client_interrupt.sendall(resp.REPLY02)

    # Waste some cycles here until we get the controllers info.
    # We don't want to proxy the device's info to the Switch
    # since it includes a MAC address.
    print("Waiting on Joy-Con Device Info")
    while True:
        jc_data = jc_itr.recv(50)
        if jc_data[1] == 0x21:
            print("Got Device Info")
            print_msg_controller(jc_data)
            break
    
    # Main loop
    print("Entering main proxy loop")
    while True:
        try:
            reply = client_interrupt.recv(50)
            print_msg_switch(reply)
        except BlockingIOError:
            reply = None
        
        if reply:
            jc_itr.sendall(reply)

        jc_data = jc_itr.recv(50)
        print_msg_controller(jc_data)
        client_interrupt.sendall(jc_data)

except KeyboardInterrupt as e:
    print("Closing sockets")

    jc_ctrl.close()
    jc_itr.close()

    switch_itr.close()
    switch_ctrl.close()

    try:
        sys.exit(1)
    except SystemExit:
        os._exit(1)

except OSError as e:
    print("Closing sockets")

    jc_ctrl.close()
    jc_itr.close()

    switch_itr.close()
    switch_ctrl.close()

    raise e