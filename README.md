# JoyConPi

An attempt at creating a Nintendo Switch Joy-Con emulator with a Raspberry Pi.

---

**This code is currently not working.**

This is likely due to incompatibilities with the Joy-Con's usage of Bluetooth 3.0's High Speed Connection. This might not be a surmountable issue.

Problems currently arise after the Nintendo Switch connects to the Raspberry Pi's open sockets (control, interrupt, and sdp sockets). After this point, the two devices are unable to communicate (bits are sent to the Switch, however, no bits are received).

If you have any ideas on how to improve this code, please open an issue or leave a PR!

---

## Getting Started

**1. Install the Prerequisites**

Run "setup.sh" as root to install the prerequisites needed to configure your Pi. Please review the contents of the script carefully since you'll be executing this code with a high level of privilege.

```
sudo ./setup.sh
```

**2. Enable BlueZ compatibility mode**

Due to some antiquated methods existing within PyBlueZ at the current time, BlueZ compatibility mode needs to enabled to allow for usage of certain functions (advertisement, etc). This can be done by adding the "-C" flag to the ExecStart property in the bluetooth service configuration.

To do so, edit the following file:

```bash
sudo nano /lib/systemd/system/bluetooth.service
```

Find the line "ExecStart=/usr/lib/bluetooth/bluetoothd" and change it to:

```
ExecStart=/usr/lib/bluetooth/bluetoothd -C
```

**3. Disable all unused BlueZ plugins to fix communication issues**

Open up the main configuration file for BlueZ by entering the following command:

```bash
sudo nano /etc/bluetooth/main.conf
```

Add the following line to the main.conf file:

```
DisablePlugins = network,input,audio,pnat,sap,serial
```

Restart the bluetooth daemon to apply these changes

```bash
sudo invoke-rc.d bluetooth restart
```

**4. Update the Raspberry Pi's Response**

Run the following command to get your MAC address

```bash
hciconfig hcio | awk '/BD Address: /{print $3}'
```

The MAC address should be in the form of XX:XX:XX:XX:XX:XX and have a mixture of letters and numbers.

The first packet sent to the Switch contains the Joy-Con's MAC address. For this project the MAC address sent in the packet will need to be updated manually. Automatic construction of this packet is a TODO once communication issues are resolved.

To update the MAC address with your Pi's own, open up the "responses.py" file and change the marked characters to the MAC address you obtained previously:

```
# This line needs to be changed. Change the chars marked with # to the letters of your MAC address.
REPLY02 = b'\x21\x05\x8E\x84\x00\x12\x01\x18\x80\x01\x18\x80\x80\x82\x02\x03\x48\x01\x02\x##\x##\x##\x##\x##\x##\x01\x01'

# EX: For a MAC address of B8:27:EB:27:B8:5E the response would be
REPLY02 = b'\x21\x05\x8E\x84\x00\x12\x01\x18\x80\x01\x18\x80\x80\x82\x02\x03\x48\x01\x02\xB8\x27\xEB\x27\xB8\x5E\x01\x01'
```

**5. Start the Joy-Con emulation server**

Run "start.sh" as root. Again, please remember to carefully check over all code being run due to the high level of privilege. This will create a Tmux session with the various debugging outputs for the Pi's bluetooth + the Joy-Con emulation server.

```bash
sudo ./start.sh
```

**6. Make your Pi discoverable**

Access the currently running Tmux session (if you haven't already) and run the following commands to make your Pi discoverable as a Joy-Con.

Access the session:

```bash
tmux attach -t joyconpi
```

Once in the session, switch to the right pane (running bluetoothctl). This can be done by pressing the prefix (default Ctrl + b) and using the arrow keys to navigate the panes. Once at the bluetoothctl pane, enter the following commands:

```bash
agent on
default-agent
scan on
discoverable on
```

Your Pi should now be discoverable as a Joy-Con! Your Switch should now try to initiate a connection if you open the controllers menu and attempt to pair a new controller.