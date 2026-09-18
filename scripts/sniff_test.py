#!/usr/bin/env python3
# WiFi beacon sniffer - patikros skriptas (kol kas tik spausdina, nieko nesaugo)

# iš scapy bibliotekos pasiimam du įrankius: sniff (gaudymui) ir Dot11Beacon (beacon kadro šablonui)
from scapy.all import sniff, Dot11, Dot11Beacon, Dot11Elt, RadioTap

# callback: sniff iškvies šią funkciją kiekvienam pagautam kadrui; kadras ateina kaip pkt
def show(pkt):
	# tikrinam ar beacon; probe ir data kadrus praleidžiam
	if pkt.haslayer(Dot11Beacon):
		try:
			ssid = pkt[Dot11Elt].info.decode() #.decode() - paima baitus ir paverčia juos tekstu pagal UTF-8
		except:
			ssid = "<decode error>"
		signal = pkt[RadioTap].dBm_AntSignal
		bssid = pkt[Dot11].addr2
		print(ssid, signal, bssid) #ssid - kintamasis kuris, identifikuoja, koks tinklas siuntė beacon ; signal - kintamasis, kuris fiksuoja signalo stiprumą

# klausom wlan1 (Alfa monitor režime); prn=show paduoda kiekvieną kadrą į show
# sustoja pagavus 10, bet kokių kadrų
sniff(iface="wlan1", prn=show, count=10)
