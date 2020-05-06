import os


class HIDGamepad():

    GAMEPAD_CLASS = "0x002508"
    SDP_UUID = "00001000-0000-1000-8000-00805f9b34fb"
    SDP_RECORD_PATH = "/joyconpi/controller"


    def __init__(self, bluetooth, alias, sdp_record_path, device_id="hci0"):

        self.bt = bluetooth

        self.bt.set_powered(True)
        self.bt.set_pairable(True)
        self.bt.set_pairable_timeout(0)
        self.bt.set_discoverable_timeout(180)

        self.bt.set_alias(alias)
        
        record = self.load_sdp_record(sdp_record_path)
        opts = {
            "ServiceRecord": record,
            "Role": "server",
            "RequireAuthentication": False,
            "RequireAuthorization": False,
            "AutoConnect": True
        }
        self.bt.register_profile(self.SDP_RECORD_PATH, self.SDP_UUID, opts)

        self.bt.set_device_class(self.GAMEPAD_CLASS)


    def load_sdp_record(self, path):
        """Loads an XML SDP record

        :param path: Path to the record
        :type path: string
        :raises OSError: On error in record load
        :return: The contents of the record
        :rtype: string
        """

        record = None
        try:
            with open(path, "r") as f:
                record = f.read()
        except e:
            raise OSError("Could not load the SDP record: %s" % str(e))
        return record
