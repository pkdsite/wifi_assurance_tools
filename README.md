# wifi_assurance_tools

CLIENT WIFI ASSURANCE TOOL

This application note is designed for a wireless assurance tool that runs on an enterprise end point, monitors the SOPHOS WIFI connectivity experience. 
The data to measure experience and troubleshoot the system is read from the WIFI driver inbuilt in the system. 
The first step is that the application need to be able to scan for access points within the range of the device and capture the results of that scan.  
Next step is that the application has to scan for the connected network.  
The connected network as well as radio scanning information is saved in the database and the information will show up on the browser(localhost) and based on this information, gauge graph is populated showing user experience and troubleshooting table is displayed.

Key Terms 
 (W)AP – (Wireless) Access Point: A device that allows the user to connect wirelessly to a network. 
  BSSID – Basic Service Set IDenitifier: This is another name for a MAC address. 
dBm or dBmW – deciBel milli-Watts: a signal strength rating in decibels as a power rating compared to 1 milliWatt 
MAC address – Media Access Address: The physical address of a network device. 
SSID – Service Set IDentifier: A name given to a network to describe it. 
Wi-Fi – Wireless Fidelity: The protocol most frequently used for wide local area networks.
RSSI - Received Signal Strength Indication: This is a dBm value that indicates the wireless signal strength received by the client and it usually ranges from 0 to -100. The higher the value, the stronger the signal, being 0 the weakest and 100 the strongest
SNR - Signal-To-Noise Ratio: This is measured in dB that is used to compare the signal received with the background noise. The higher the value, the better the communication quality.
Channel - Network operating channel. If the network is operating over more than one channel, all operating channels are displayed here.
DHCP – Dynamic Hosting Configuration Protocol: This is a network management protocol used to dynamically allocate an Internet address to any device or any node on a network.
DNS – Dynamic Naming System: An Internet service that translates domain names into IP addresses.
Gateway – A gateway is a hardware device that acts as a “gate” between two networks.
Latency - It is the time required to transmit the packet from host to destination in a network. It can be measured in one way or roundtrip.
Jitter – It defines the variation in the delay of received packets.
Throughput – It defines the quantity of data being sent or received per unit time.


Introduction
Wi-Fi is a critical resource of businesses of all types and sizes. It is no longer the exclusive domain of larger enterprise or home networks. Whether it is a retail shop or a five-person startup the reliability of the Wi-Fi connectivity is an important connectivity factor. At the same time, the challenges in delivering consistent Wi-Fi performance and availability continue to grow. This include technical factors such as increased usage driven congestion as well as organizational factors like lack of expertise or resources in the business to manage Wi-Fi.

Objectives
The purpose of the application is to check and verify WIFI parameters related to layer1 and layer 2 which include basic ping test for above layers entities (RADIUS server, DNS server, DHCP server and Gateway) to ensure proper working of WIFI. Based on radio scanning and ping test, gauge graph and troubleshooting table would populate indicating user experience and Wi-Fi parameters respectively.


Deployment
The technologies involved in the project consists of a database equipped with frontend support which can scan the radio signals around the system and store the scanned data properly in the database. 
First, we need to start the node server by running the node script which specifies the port information. The script also has a python script running in background scanning the radio signals & current scanning and storing in the specified SQLite database. This DB is created automatically by the python script. 
	Next, we make calls to retrieve the parameters stored in the SQLite database and give it to frontend as JSON object. JSON are portable and easy medium of transferring data through web. This JSON is handled by the frontend code which is totally written in Angular JS.  
Now to deploy the project, make sure you have downloaded all the files with the folder hierarchy preserved & maintained and perform following steps in order:


Installations on Windows:
•	Install Python3.x from https://www.python.org/downloads/. Add it to your path as environment variable.
•	Install any code editor or preferably Visual Studio Code.
Visit https://code.visualstudio.com/. 
•	Download SQLite from “https://www.sqlite.org/download.html” and follow the instructions given at https://www.tutorialspoint.com/sqlite/sqlite_installation.htm for installation.
Type sqlite3 in command prompt to check if it’s working. 
•	Install Node JS from https://nodejs.org/en/download/. Add this also to your path as environment variable.
•	Install node package manager and initialize required packages by typing “npm init” in the windows command prompt shell. This generates a package.json file with necessary dependencies to be installed.
•	For executing Python scripts in node JS file, we need node package manager “npm” to install python-shell package in node. Open windows command prompt and type “npm i python-shell”.
•	In the same prompt execute “npm install sqlite3 express” to install corresponding dependencies.

After all the dependencies have been installed, open the directory where the code files are present.
•	Move the index.html and logic.js files into public folder.
•	Run the Node JS Server file which starts a server in specified port.
Open a command prompt and type
	“node server.js “ 
•	 This server JS file has a python script which can scan the radio signals and store in SQLite3 database.
•	The python script has terminal command “netsh wlan show net mode=bssid” for radio scanning and “netsh wlan show interface” for current scanning which are executed in the background.
•	Now open the index.html file on the specified port as,
             “ http://localhost:8080/index.html ”
•	Now the webpage loads up. Press the Scan button to view the results.
