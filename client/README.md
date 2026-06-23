# Melomania clients

Clients talk to the daemon over the **DBus session bus**
(`com.meloadapter.MeloControl`): they call `SendCommand(feature, subfeature,
payload)` and react to the `CommandReceived` signal. The boundary is plain
strings (e.g. `"MODE"`, `"SET_GAMING_MODE"`, `"1"`), so clients never touch the
wire format — that all lives in the daemon.

Start the daemon first (from the repo root):

```bash
python daemon/linux.py
```

## GTK GUI

`gui.py` — a reactive GTK4/libadwaita window. Each incoming packet is routed by
its subfeature name to the control that owns it and updates it live; values are
decoded through the `parsers/` package. It auto-refreshes all values on connect
and shows a live connection status pill.

```bash
python client/gui.py
```

Requires PyGObject with GTK 4 + libadwaita 1 (`gi`) and `dbus-python`.

## Curses TUI

`linux.py` — the original minimal terminal client (manual `send <feature>
<subfeature> [payload]` commands, raw RX log).

```bash
python client/linux.py
```