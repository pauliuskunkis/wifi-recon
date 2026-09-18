#!/usr/bin/env python3
# WiFi beacon sniffer

from scapy.all import sniff, Dot11, Dot11Beacon, Dot11Elt, RadioTap
import sqlite3
from datetime import datetime

# open the database once
conn = sqlite3.connect("captures.db")
cur = conn.cursor()

# callback: sniff call the function for every capture as pkt
def show(pkt):
	# checking for becon
	if pkt.haslayer(Dot11Beacon):
		try:
			ssid = pkt[Dot11Elt].info.decode() #.decode() - takes the bites and converts them with UTF-8
		except:
			ssid = "<decode error>"
		signal = pkt[RadioTap].dBm_AntSignal
		bssid = pkt[Dot11].addr2
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# stores the row = ? placeholders keeps untrusted SSID safe from injections
		cur.execute(
			"INSERT INTO networks (timestamp, bssid, ssid, signal) VALUES (?, ?, ?, ?)", (timestamp, bssid, ssid, signal)
        )
	conn.commit()

		#ssid - variable for network name who sent beacon; signal - variable for strenght of beacon; bssid - variable for mac address
	print(ssid, signal, bssid)

# Listens wlan1 in monitor mode; prn=show sent every capture to show; count=10 amount of captures;
sniff(iface="wlan1", prn=show, count=10)

conn.close() # close when sniff finishes
