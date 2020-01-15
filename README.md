# JoyConPi

An attempt at creating a Nintendo Switch Joy-Con emulator with a Raspberry Pi.

---

**This code is currently not working.**

This is likely due to incompatibilities with the Joy-Con's usage of Bluetooth 3.0's High Speed Connection. This might not be a surmountable issue.

Problems currently arise after the Nintendo Switch connects to the Raspberry Pi's open sockets (control, interrupt, and sdp sockets). After this point, the two devices are unable to communicate (bits are sent to the Switch, however, no bits are recieved).

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

**4. Start the Joy-Con emulation server**

Run "start.sh" as root. Again, please remember to carefully check over all code being run due to the high level of privilege. This will create a Tmux session with the various debugging outputs for the Pi's bluetooth + the Joy-Con emulation server.

```bash
sudo ./start.sh
```

**5. Make your Pi discoverable**

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