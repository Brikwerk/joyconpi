#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <errno.h>

#include <glib.h>
#include <gio/gio.h>

#include "org-bluez-adapter1.h"

int main (int argc, char *argv[])
{
    GError *error = NULL;
    OrgBluezAdapter1 *proxy;

    proxy = org_bluez_adapter1_proxy_new_for_bus_sync(
        G_BUS_TYPE_SYSTEM,
        G_DBUS_PROXY_FLAGS_NONE,
        "org.bluez",
        "/org/bluez/hci0",
        NULL,
        &error
    );

    if (proxy == NULL) {
        g_print ("Failed to initialize the D-Bus: %s\n", error->message);
        return -1;
    }

    const gchar *name = org_bluez_adapter1_get_name(proxy);
    if (!name) {
        g_print("Failed to get adapter name.\n");
        g_print("The proxy's name/object path is likely wrong.\n");
        return 0;
    } else {
        g_print("Name of Device: %s\n", name);
    }

    const gchar *address = org_bluez_adapter1_get_address(proxy);
    g_print("BT MAC Address of Device: %s\n", address);

    // Defaults to 3 minutes. If set to 0, makes timer infinite
    // guint timeout = 0;
    // org_bluez_adapter1_set_discoverable_timeout(proxy, timeout);

    gboolean discoverable = TRUE;
    org_bluez_adapter1_set_discoverable (proxy, discoverable);

    return 0;
}