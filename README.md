# OpenVPN-Connect
VPN connection to the selected profile from the existing ones on the vpnbook.com

VPN connection to the selected profile from the existing ones on the vpnbook.com
----------

### Features:
1. Obtaining vpn profiles specified on the vpnbook.com;
2. Getting a username and password to connect;
3. It allows you to select a profile and then sets it in the system;
4. The program allows you to select a profile, installs it into the system and activate the connection.

### Necessary conditions for the program to work:
1. **GOCR** OCR software installed on the system (in Ubuntu: `sudo apt install gocr`);
2. Installed **Network Manage** on the system (in Ubuntu: `sudo apt install network-manager`);
3. Installed Python modules:
   1. `enquiries` - used to display the selection menu;
   2. `beautifulsoup4` - parsing the site;
   3. `lxml` - processing XML and HTML

To install the required modules, you can run the command:<br>
`pip3 install -r requirements.txt`<br>
or install them separately:<br>
`pip3 install <module_name>`
