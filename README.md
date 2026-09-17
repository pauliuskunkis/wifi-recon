# kami-pi — Portable WiFi Logging Device

> A headless Raspberry Pi that passively listens to nearby WiFi management
> frames and logs what's around it — built to learn Linux, networking, and
> wireless security hands-on.

	## Overview
	kami-pi runs a second WiFi adapter in monitor mode to capture the 802.11
	management frames that nearby devices and access points broadcast — the same
	beacons your phone reads when it shows a list of networks. It records which
	access points are around, plus their signal strength, channel, and encryption,
	so the environment can be mapped. Everything is passive: it only listens to
	public broadcast frames and never connects to or decrypts anything.

	## Hardware
	- Raspberry Pi 4 Model B (2 GB RAM), Raspberry Pi OS Lite (64-bit / ARM64),
	  running headless over SSH.
	- Alfa AWUS036ACS USB adapter (Realtek RTL8811AU chipset). Chosen because it
	  is dual-band (2.4 + 5 GHz) and its chipset supports monitor mode — a normal
	  built-in WiFi card usually cannot be put into monitor mode, which is the
	  core requirement here.
	- 20000mAh USB-C power bank (5V/3A) for portable use, GPIO active cooling fan,
	  32 GB microSD.

	## Architecture
	The Pi uses two separate radios at the same time:
	- `wlan0` — the Pi's built-in WiFi. It stays connected to my home router and carries my SSH session and internet. I never touch it; if it drops, I lose remote 	access to the device.
	- `wlan1` — the Alfa adapter. This is the one I swi	tch into monitor mode to capture frames.

	Two radios matter because a radio in monitor mode can't also act as a normal client on my network. With only one radio, putting it into monitor mode would kill 	my own connection to the Pi. With two, `wlan0` keeps me connected and in control while `wlan1` does the listening — management and capture at once, without 	interfering.

	## Setup
	1. Flash Raspberry Pi OS Lite (64-bit), enable SSH, connect over `wlan0`.
	2. `sudo apt update && sudo apt full-upgrade`, then reboot.
	3. Install capture tools: `sudo apt install aircrack-ng iw`.

	Note on the driver: most guides tell you to download and compile an out-of-tree Realtek driver. On a current kernel that is unnecessary — the OS already ships 	an in-kernel driver (`rtw88_8821au`) that supports this chipset and handles monitor mode natively. I just plug the adapter in and it works. (See "Notable 	problem solved" for why.)

	## Usage
		### Enabling monitor mode
		Switch only `wlan1` into monitor mode without dropping SSH on `wlan0`:
		sudo nmcli device set wlan1 managed no
		sudo ip link set wlan1 down
		sudo iw dev wlan1 set type monitor
		sudo ip link set wlan1 up

		Then start capturing:
		sudo airodump-ng wlan1

		Important: I don't use `airmon-ng check kill` — it stops NetworkManager entirely, which would drop `wlan0` and kick me out of my own SSH session. The 		commands above touch only `wlan1`.

		### Running the logger script
		`sniff_test.py` is a Python script that captures the beacon frames broadcast by nearby access points, extracts each network's name (SSID) and signal 		strength, and prints them. Run it with `sudo ./sniff_test.py` — it stops after 10 captured frames. It has basic error handling: if an SSID contains 		bytes that can't be decoded as UTF-8, the script catches the error and keeps running instead of crashing.

	## The logger script
	The script uses scapy to sniff frames on `wlan1` and processes each one:
	- **Beacons only:** it filters for beacon frames and ignores probe requests and data frames, so it only logs access points that are actually broadcasting.
	- **Decoding the name:** the SSID comes in as raw bytes, so it's decoded to readable text (UTF-8).
	- **Error handling:** the decode is wrapped in try/except. Real WiFi traffic includes networks with hidden or non-text SSIDs that can't be decoded — without 	this guard, one bad frame would crash the whole capture. Since the logger is meant to run unattended for hours, it has to survive messy data.
	- **Status:** currently prints to screen only; writing to CSV/SQLite is next.

	## Notable problem solved: the driver
	Following the common advice, I first tried to compile the out-of-tree `aircrack-ng/rtl8812au` driver with DKMS, and the build failed. It wasn't out of memory 	or a bug in the driver's logic — the compiler couldn't find the driver's own header files. Root cause: the driver's build files point the compiler to those 	headers using a kernel build variable (`$(src)`) whose meaning changed around kernel 6.13. My Pi runs kernel 6.18, so the 2019-era driver was pointing the 	compiler at the wrong place. Rather than patch that (which would only lead to the next incompatibility), I found that the driver's own maintainer now 	recommends the in-kernel `rtw88` driver for kernel 6.14+ — which is also better, because it does monitor mode the standard (mac80211) way. I dropped the out-	of-tree driver and used the in-kernel one: nothing to compile, better supported.

	## Ethics & scope
	Passive only, on my own hardware and network (or legal labs). I capture publicly broadcast management frames — the same ones any phone receives to list 	networks. I do not connect to networks I don't own, decrypt traffic, de-auth, or track individuals.

	## Status & roadmap
	- Done: in-kernel driver, monitor mode, airodump-ng mapping working.
	- Next: Python + scapy logger writing frames to SQLite/CSV; systemd autostart.
	- Ideas: GPS wardriving, Pi-hole, WireGuard VPN, monitoring stack (Prometheus / Grafana).

	## What I learned (setup)
	- Popular guides can be outdated. The standard "compile this driver" advice was wrong for my kernel; reading the actual error and the maintainer's own notes 	led to a simpler, better solution.
	- On a headless device, a careless network change can lock you out. Isolating one interface is far safer than killing the whole network manager.
	## What I learned (script)
	- Setting up and running a Python script on a headless Pi (shebang, `chmod +x`, running with `./` and `sudo`).
	- Keeping the project organized in a clear folder structure.
	- How Python uses indentation for structure — and why mixing tabs and spaces breaks it.
	- The difference between a variable and a function.
	- Handling bad input with try/except so the program doesn't crash.
	- Using scapy's building blocks: `sniff`, `Dot11Beacon`, `Dot11Elt`, `RadioTap`.
