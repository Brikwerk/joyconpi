def print_msg(data, split, name):
    """Prints a given byte message in hex format split
    into payload and subcommand sections.

    :param data: A series of bytes
    :type data: bytes
    :param split: The location of the payload/subcommand split
    :type split: integer
    :param name: The name featured in the start/end messages
    :type name: string
    """

    payload = ""
    subcommand = ""
    for i in range(0, len(data)):
        if i <= split:
            payload += "0x" + str(hex(data[i]))[2:].upper() + " "
        else:
            subcommand += "0x" + str(hex(data[i]))[2:].upper() + " "
    
    print(f"--- Start {name} Msg ---")
    print(f"Payload:    {payload}")
    print(f"Subcommand: {subcommand}")
    print(f"--- End {name} Msg ---")


def print_msg_controller(data):
    """Prints a formatted message from a controller

    :param data: The bytes from the controller message
    :type data: bytes
    """

    print_msg(data, 13, "Controller")


def print_msg_switch(data):
    """Prints a formatted message from a Switch

    :param data: The bytes from the Switch message
    :type data: bytes
    """

    print_msg(data, 10, "Switch")
