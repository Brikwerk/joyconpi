import subprocess
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom


DBUS_XML_HEADER = '<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN" \
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">\n'
BLUEZ_VERSION = subprocess.run(["bluetoothd", "--version"], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()


def write_new_dbus_xml(element):
    root = ET.Element("node")
    root.insert(0, element)
    xml_name = element.attrib["name"] + ".xml"
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    xml_str = xml_str.replace('<?xml version="1.0" ?>', '')
    with open(xml_name, 'w') as f:
        f.write(DBUS_XML_HEADER)
        f.write(f"<!-- Extracted on BlueZ v{BLUEZ_VERSION} -->\n")
        f.write(xml_str)


def main():
    # dbus-send arguments for the two main BlueZ objects
    org_bluez_args = [
        "dbus-send", 
        "--system",
        "--dest=org.bluez",
        "--type=method_call",
        "--print-reply",
        "/org/bluez",
        "org.freedesktop.DBus.Introspectable.Introspect"
    ]
    org_bluez_hci0_args = [
        "dbus-send", 
        "--system",
        "--dest=org.bluez",
        "--type=method_call",
        "--print-reply",
        "/org/bluez/hci0",
        "org.freedesktop.DBus.Introspectable.Introspect"
    ]

    # Getting results from dbus-send
    org_bluez_result = subprocess.run(org_bluez_args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    org_bluez_hci0_result = subprocess.run(org_bluez_hci0_args, stdout=subprocess.PIPE).stdout.decode('utf-8')

    # Cleaning results
    org_bluez = re.sub('method (.*)\n   string "', "", org_bluez_result[0:len(org_bluez_result)-2])
    org_bluez_hci0 = re.sub('method (.*)\n   string "', "", org_bluez_hci0_result[0:len(org_bluez_hci0_result)-2])

    # Parsing XML
    org_bluez_root = ET.fromstring(org_bluez)
    org_bluez_hci0_root = ET.fromstring(org_bluez_hci0)

    # Saving interfaces as XML
    for child in org_bluez_hci0_root:
        if (child.tag == "interface"):
            if ("freedesktop" not in child.attrib["name"]):
                child_xml = write_new_dbus_xml(child)
    
    for child in org_bluez_root:
        if (child.tag == "interface"):
            if ("freedesktop" not in child.attrib["name"]):
                child_xml = write_new_dbus_xml(child)


if __name__ == "__main__":
    main()