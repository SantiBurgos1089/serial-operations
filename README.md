# serial-operations

Handle some operations from the RS232 serial port on Linux environments. For now the repo is focused on the following operations:

* Serial monitor (based on the Windows app "freeserialmonitor")
* Websocket

## Requirements

### Frontend

* GTK4
* libAdapta or libAdwaita
* Python >= 3.10 (using Debian 13 as a base)

### Backend

* asyncio
* pyserial
* GObject
* GLib
* libnotify
* Python >= 3.10 (using Debian 13 as a base)
* [xapp-symbolic-icons](https://github.com/xapp-project/xapp-symbolic-icons)
