import subprocess

import dbus


class BlueZ():
    """Exposes the BlueZ D-Bus API as a Python object.
    """

    SERVICE_NAME = "org.bluez"
    ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"

    def __init__ (self, device_id="hci0"):
        self.bus = dbus.SystemBus()

        # Try to find the default adapter (hci0) or a user specified adapter
        adapter_path = self.find_object_path(self.SERVICE_NAME, self.ADAPTER_INTERFACE,
            object_name=device_id)
        
        # If we aren't able to find an adapter
        if adapter_path == None:
            adapter_error = "Unable to find a bluetooth adapter"
            if device_id:
                adapter_error += f" with a device ID of {device_id}"
            raise Exception(adapter_error)
        
        # Load the adapter's interface for later use
        print(f"Using adapter under object path: {adapter_path}")
        self.adapter = dbus.Interface(self.bus.get_object(self.SERVICE_NAME, adapter_path),
            "org.freedesktop.DBus.Properties")
        
        if device_id:
            self.device_id = device_id
        else:
            self.device_id = adapter_path.split("/")[-1]
    

    def find_object_path(self, service_name, interface_name, object_name=None):
        """Searches for a D-Bus object path that contains a specified interface
        under a specified service.

        :param service_name: The name of a D-Bus service to search for the
        object path under.
        :type service_name: string
        :param interface_name: The name of a D-Bus interface to search for
        within objects under the specified service.
        :type interface_name: string
        :param object_name: The name or ending of the object path, defaults to None
        :type object_name: string, optional
        :return: The D-Bus object path or None, if no matching object can be found
        :rtype: string
        """
        
        manager = dbus.Interface(self.bus.get_object(service_name, "/"), 
            "org.freedesktop.DBus.ObjectManager")

        # Iterating over objects under the specified service
        # and searching for the specified interface
        for path, ifaces in manager.GetManagedObjects().items():
            managed_interface = ifaces.get(interface_name)
            if managed_interface is None:
                continue
            # If the object name wasn't specified or it matches
            # the interface address or the path ending
            elif (not object_name or 
                    object_name == managed_interface["Address"] or
                    path.endswith(object_name)):
                obj = self.bus.get_object(service_name, path)
                return dbus.Interface(obj, interface_name).object_path

        return None


    @property
    def address(self):
        """Gets the Bluetooth MAC address of the Bluetooth adapter.

        :return: The Bluetooth Adapter's MAC address
        :rtype: string
        """

        return self.adapter.Get(self.ADAPTER_INTERFACE, "Address")
    

    @property
    def name(self):
        """Gets the name of the Bluetooth adapter.

        :return: The name of the Bluetooth adapter.
        :rtype: string
        """

        return self.adapter.Get(self.ADAPTER_INTERFACE, "Name")
    

    @property
    def alias(self):
        """Gets the alias of the Bluetooth adapter. This value is used
        as the "friendly" name of the adapter when communicating over
        Bluetooth.

        :return: The adapter's alias
        :rtype: string
        """

        return self.adapter.Get(self.ADAPTER_INTERFACE, "Alias")


    def set_alias(self, value):
        """Asynchronously sets the alias of the Bluetooth adapter.
        If you wish to check the set value, a time delay is needed
        before the alias getter is run.

        :param value: The new value to be set as the adapter's alias
        :type value: string
        """

        self.adapter.Set(self.ADAPTER_INTERFACE, "Alias", value)


    @property
    def pairable(self):
        """Gets the pairable status of the Bluetooth adapter.

        :return: A boolean value representing if the adapter is set as
        pairable or not
        :rtype: boolean
        """

        return bool(self.adapter.Get(self.ADAPTER_INTERFACE, "Pairable"))


    def set_pairable(self, value):
        """Sets the pariable boolean status of the Bluetooth adapter.

        :param value: A boolean value representing if the adapter is
        pairable or not.
        :type value: boolean
        """

        dbus_value = dbus.Boolean(value)
        self.adapter.Set(self.ADAPTER_INTERFACE, "Pairable", dbus_value)


    @property
    def pairable_timeout(self):
        """Gets the timeout time (in seconds) for how long the adapter
        should remain as pairable. Defaults to 0 (no timeout).

        :return: The pairable timeout in seconds
        :rtype: int
        """

        return self.adapter.Get(self.ADAPTER_INTERFACE, "PairableTimeout")

    
    def set_pairable_timeout(self, value):
        """Sets the timeout time (in seconds) for the pairable property.

        :param value: The pairable timeout value in seconds
        :type value: int
        """

        dbus_value = dbus.UInt32(value)
        self.adapter.Set(self.ADAPTER_INTERFACE, "PairableTimeout", dbus_value)


    @property
    def discoverable(self):
        """Gets the discoverable status of the Bluetooth adapter

        :return: The boolean status of the discoverable status
        :rtype: boolean
        """

        return bool(self.adapter.Get(self.ADAPTER_INTERFACE, "Discoverable"))
    

    def set_discoverable(self, value):
        """Sets the discoverable boolean status of the Bluetooth adapter.

        :param value: A boolean value representing if the Bluetooth adapter
        is discoverable or not.
        :type value: boolean
        """

        dbus_value = dbus.Boolean(value)
        self.adapter.Set(self.ADAPTER_INTERFACE, "Discoverable", dbus_value)


    @property
    def device_class(self):
        """Gets the Bluetooth class of the device. This represents what type
        of device this reporting as (Ex: Gamepad, Headphones, etc).

        :return: A 32-bit hexadecimal Integer representing the 
        Bluetooth Code for a given device type.
        :rtype: string
        """

        # This is another hacky bit. We're using hciconfig here instead
        # of the D-Bus API so that results match the setter. See the
        # setter for further justification on using hciconfig.
        result = subprocess.run(["hciconfig", self.device_id, "class"],
            stdout=subprocess.PIPE)
        device_class = str(result.stdout).split("Class: ")[1][0:8]

        return device_class


    def set_device_class(self, device_class):
        """Sets the Bluetooth class of the device. This represents what type
        of device this reporting as (Ex: Gamepad, Headphones, etc).

        :param device_class: A 32-bit Hexadecimal integer
        :type device_class: string
        """

        # This is a bit of a hack. BlueZ allows you to set this value, however,
        # a config file needs to filled and the BT daemon restarted. This is a
        # good compromise but requires super user privileges. Not ideal.
        result = subprocess.run(["hciconfig", self.device_id, 
            "class", device_class])


    @property
    def powered(self):
        """The powered state of the adapter (on/off) as a boolean value.

        :return: A boolean representing the powered state of the adapter.
        :rtype: boolean
        """

        return bool(self.adapter.Get(self.ADAPTER_INTERFACE, "Powered"))


    def set_powered(self, value):
        """Switches the adapter on or off.

        :param value: A boolean value switching the adapter on or off
        :type value: boolean
        """

        dbus_value = dbus.Boolean(value)
        self.adapter.Set(self.ADAPTER_INTERFACE, "Powered", dbus_value)
