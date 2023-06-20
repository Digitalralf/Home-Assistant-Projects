# Two Zigbee Networks joined over a Wireguard VPN
This post is written as part of an assignment for the HAN University of Applied Sciences. This is also part of a few other guides I am posting.
Other guides can be found here:

Controlling Tuya devices locally using Node-Red: `TBD`

Connecting long range sensors using LoRa and MQTT:`TBD`

This guide presumes that you have some basic knowledge of using Home-Assistant and network interaces in general and that Home-Assistant is already installed. I am not liable for broken devices, broken configuration, thermonuclear war or ANYTHING ELSE. This guide is provided as is, but feel free to comment on mistakes, inaccuracies and please give suggestions to add to this guide. Nonetheless I hope you find it interesting :D

# Introduction

A few years ago I moved out from my parents home into my own studio. Thats when I also decided that I wanted to install Home-Assistant and make my studio smart. It started with a couple of Zigbee lightbulbs from the Lidl and a Raspberry Pi running Home-Assistant. However I also had a small smarthome setup using and ESP8266 with [Blynk](https://blynk.io/getting-started). Which controlled my lights and an LED-Strip at my parents house. Since I visit my parents regularly I wanted to connect that blynk project to my smarthome. At first I used Node-Red to interface with blynk, but at a certain point it was clear that I had to make new firmware since the original blynk implementation was going to be deprecated since it was a cloud solution. So I wanted to install ESPHome onto that ESP8266, but ESPHome is local and I wanted a secure connection. So I opted to make a VPN-Bridge using Wireguard and two OpenWRT routers. Wireguard can be installed on OpenWRT using its own package manager and is very lightweight. Later I also wanted to have Zigbee devices and sensors on the other side. So I connected a networked Zigbee gateway at my parents home.

## WireGuard
Wireguard is a very simple and lightweight VPN that uses cryptography with public and private keys. If you are familiar with SSH-Keys and such than this guide is going to be a lot easier to follow. More information on wireguard can be found [here](https://www.wireguard.com/)

## OpenWRT
OpenWRT is an open-source router OS based on Linux. It can be installed on variety of routers and gives you more control over your own network. More information can be found [here](https://openwrt.org/). If you have further questions about OpenWRT I suggest looking at their forum [here](https://forum.openwrt.org/)

## Zigbee
Zigbee is a smarthome mesh protocol. It can be used to control all sorts of smart devices. If you don't know what Zigbee is you can follow along this guide since the Zigbee part is mostly plug and play with the right hardware. However I do recommend for you to read up on what zigbee is in a basic form. A good article on Zigbee can be found [here](https://www.techtarget.com/iotagenda/definition/ZigBee).

# Prerequisites
For this project quite some hardware is needed so some costs are involved, but OpenWRT routers can be bought fairly cheap on second hand. There is also a Wireguard plugin in Home-Assistant, however we won't be using the wireguard implementation there since this guide aims to have two seperate networks joined together from a routers point of view. From Home-Assistants point of view everything looks like one giant network and all Add-Ons and integrations can make use of this very easy without any other configurations necessary.

## Hardware needed
For this project we need two Zigbee gateways and two routers to join the Zigbee networks.

### Routers
The Routers need to be compatible with OpenWRT. If you already have two routers look at [this](https://openwrt.org/supported_devices) to see if there is an OpenWRT implementation for it. If you don't have a router and don't want to spend to much money I would suggest you find a cheap easy to install in that list. Typically Linksys or TP-link routers work very well with OpenWRT, but make sure to double check the model number.

### Zigbee gateways
For this project you need two zigbee gateways which do have some requirements. Unfortunately you can't just get two of the same Zigbee gateways and call it a day. Since ZHA doesn't allow for two separate instances with two different gateways we have to use two separate Zigbee integrations for this. I use Deconz and ZHA. Deconz requires you to use the Conbee II stick. ZHA can use a lot of gateways, but for our case it is required to use a **NETWORKED** gateway. Since that is the whole point of setting up WireGuard. I have used a Lidl Zigbee Gateway that I have put different firmware on according to [this](https://paulbanks.org/projects/lidl-zigbee/ha/) guide. I understand that this isn't feasible for almost everyone. An example of a of the shelf gateway that would probably work is the wireless sonoff zigbee gateway (ZBBridge).

## Used Home-Assistant integrations
The Zigbee gateways have to have its own integrations.
### Deconz
Deconz is developed by dresden elektronik. It is the main peace of software we need to control our Zigbee setup at the server side. More information can be found [here](https://www.home-assistant.io/integrations/deconz/)
### Zigbee Home Automations
Zigbee home automation or ZHA in short is used to control the Zigbee network at the "client" side of the router. More information on ZHA can be found [here]()
## Example Setup
In this guide I am going to reference my own setup a lot. My Own setup looks something like this:

<img src="./pics/Network.png" alt="Personal WireGuard Setup" width="50%" height ="50%">

While wireguard itself doesn't use server and client terminology, but always talks about peers. This setup is using a "server client" configuration. Where the router in my studio is used as a "server". The only difference is that the Server needs a port directly to access the internet. However this is safe since all data is encrypted and there is no direct access from the outside to either routers.

I opted to do it in this way since the "client" peer is behind another router that is used by my parents. I have also set it up this way so I don't have access to my parents devices remotely from my studio and other smart devices since I respect their privacy.

Many thanks to the people who originally helped me on the OpenWRT Forums: [Gopten](https://forum.openwrt.org/u/gopten/summary) and [vgaetera](https://forum.openwrt.org/u/vgaetera/summary).
Link to the original thread where I asked on the OpenWRT forum can be found [here](https://forum.openwrt.org/t/connect-two-routers-with-a-vpn-over-the-internet/114216/4)

# Step 1 - Install OpenWRT
This step is highly dependent on your own setup. I recommend to visit the OpenWRT Supported devices page and look up your router and compatibility [here](https://openwrt.org/supported_devices) and look at the Table of Hardware Section. If you don't have a router yet I would suggest to get a compatible one and look at the installation steps first. It is easiest to get two of the same routers since that makes the installation process same twice.

## Example Setup
In my own setup I used two TP-Link Archer C7 (AC1750) Ver 5.0. The support page mentioned that the firmware can be installed using the firmware uploader in TP-Links own software. So that is what we will do. Do note that there are different versions of this router so keep that in mind everything from V2.0 to V5.0 should be fine. Just download the right one for your router. I have the V5.0 So that is what i'll be using

This tutorial on Youtube is for the Archer A7 but describes the same setup for using the TP-Link interface. If you prefer video you can watch it [here](https://www.youtube.com/watch?v=wrREvRUD9Ng) All credits go to **Behfor**.

The steps I used are the same but I will give a brief summary here:

1. Download the OpenWRT `factor.bin` and `sysupgrade.bin` for your router.
2. Go to your TP-Link Router page by going to the IP-Address of your router usually something like `192.168.0.1` or `192.168.1.1`
3. Go to `Advanced -> System Tools -> Firmware Upgrade` Upload the OpenWRT `factory.bin` and wait.
4. Go to the router page again `192.168.1.1` is standard for OpenWRT. And you should be greeted with a login prompt for OpenWRT. Set your password for OpenWRT
5. Go to `System -> Backup/ Flash Firmware -> Flash new firmware image` Here you should upload the `sysupgrade.bin`. OpenWRT should now be installed. Congratulations you have OpenWRT
6. Since you are going to connect the routers It is important that the IP-addresses that the routers are going to use are different for each network. Go to `Interfaces -> LAN -> Edit -> IPv4 Address` and change the ip address to something other than `192.168.1.X`.\
   For example you can use `192.168.2.1`. I use `192.168.3.1` since the `2`one is already in use in my own network.

# Step 2 - Install and Setup Wireguard
Installing Wireguard is probably the most difficult thing to do in this guide. This part is a mirror of [this](https://openwrt.org/docs/guide-user/services/vpn/wireguard/server) guide. But I am aiming to give some more explanation on what this guide is doing. Feel free to correct any information that might be wrong. 

So I am going to give some explanation on what we are doing here. You can skip this, but I would not recommend it. Wireguard uses a public and private key cryptography combination in order for secure communication between peers. Every peer has its own pair of  aprivate key and a public key. This kind of cryptography is also used very widely in SSH and HTTPS for example. Additionally we are also going to generate a pre-shared key for a layer of extra security. While it is not necessary it is not harder to add this to the setup and is also used in the guide above

**WARNING DO NOT SHARE THE PRIVATE AND PRESHARED KEYS THAT ARE ABOUT TO BE GENERATEd. DO NOT POST THEM. DO NOT SEND THEM OVER THE INTERNET. THE BEST METHOD IS STORE THEM LOCALLY OR EVEN WRITE THEM DOWN BY HAND AND ERASE THEM LATER. LEAKING THESE KEYS WILL DEFEAT THE POINT OF SECURITY**

Before we are going to place both routers at different locations connected to the internet. I Would suggest to connect the routers first and later change the IP-Address for where wireguard has to connect to. This way you don't have to move or drive somewhere everytime something goes wrong.\
Every Step here is described by using the commandline of OpenWRT. So we have to enable SSH so we have access to our router from a pc.\
To enable SSH in the routers interface we go to `System -> Administration -> SSH Acess` Here you can turn on SSH access.\
**DO NOT SET YOUR ACCESS TO WAN ON PORT 22 WITHOUT A PASSWORD.**\
Set the `Interface` to `lan` and choose a port. Port `22` is standard. Tick `Allow SSH password authentication` and `Allow root logins with password`. We are only logging in from our own network. Beware that anyone who know the password of your router and is connected to your Wifi or Ethernet can login into your router this way.

Open up a terminal client on Windows,Mac or Linux and type in `ssh root@"Your routers ip-address"` Most of the time it will look like this `ssh root@192.168.1.1`\
Type your password and you should be welcomed by something like this. (I have obfuscated some information)

```bash
BusyBox vX.XX (XXXX-XX-XX XX:XX:XX UTC) built-in shell (ash)

  _______                     ________        __
 |       |.-----.-----.-----.|  |  |  |.----.|  |_
 |   -   ||  _  |  -__|     ||  |  |  ||   _||   _|
 |_______||   __|_____|__|__||________||__|  |____|
          |__| W I R E L E S S   F R E E D O M
 -----------------------------------------------------
 OpenWrt XX.XX.X, ....
 -----------------------------------------------------
root@OpenWrt:~#
```
From here we can move to either client or server setup.
## Server Setup:
1.  We have to update our packages and install wireguard. OpenWRT has its own package manager `opkg`\
    To do this we have to enter:
    ```bash
    opkg update
    opkg install wireguard-tools    
    ```
    This can also be done in the router interface by going to `System -> Software` And looking for the package name there

2.  Next we need to enter the configuration parameters. Here we are defining some environment variables we are going to use later
    ```bash
    VPN_IF="vpn"
    VPN_PORT="51820"
    VPN_ADDR="192.168.9.1/24"
    VPN_ADDR6="fd00:9::1/64"
    ```
    You can also write them down. Would not recommend it though.

3.  Now we need to generate keys. **Be careful with sharing these keys**\
    ```bash
    # Generate keys
    umask go=
    wg genkey | tee wgserver.key | wg pubkey > wgserver.pub
    wg genkey | tee wgclient.key | wg pubkey > wgclient.pub
    wg genpsk > wgclient.psk
    
    # Server private key
    VPN_KEY="$(cat wgserver.key)"
    
    # Pre-shared key
    VPN_PSK="$(cat wgclient.psk)"
    
    # Client public key
    VPN_PUB="$(cat wgclient.pub)"
    ```
    These keys cannot be generated in the interface.
    Print the keys out to the terminal by using `cat wgclient.psk` and `cat wgclient.pub`. Store these keys we are going to need them for the client setup. Leave `wgserver.key` alone this is private key and should **NEVER** be shared.

4.  Now we are going to set firewall rules. 
    These can be set by using
    ```bash
    uci rename firewall.@zone[0]="lan"
    uci rename firewall.@zone[1]="wan"
    uci del_list firewall.lan.network="${VPN_IF}"
    uci add_list firewall.lan.network="${VPN_IF}"
    uci -q delete firewall.wg
    uci set firewall.wg="rule"
    uci set firewall.wg.name="Allow-WireGuard"
    uci set firewall.wg.src="wan"
    uci set firewall.wg.dest_port="${VPN_PORT}"
    uci set firewall.wg.proto="udp"
    uci set firewall.wg.target="ACCEPT"
    uci commit firewall
    /etc/init.d/firewall restart
    ```
    These can also be set from the router interface by going to `Network -> Firewall -> Add` and filling in the fields by hand.

5.  We now have configure the network settings for keys and peers
    ```bash
    # Configure network
    uci -q delete network.${VPN_IF}
    uci set network.${VPN_IF}="interface"
    uci set network.${VPN_IF}.proto="wireguard"
    uci set network.${VPN_IF}.private_key="${VPN_KEY}"
    uci set network.${VPN_IF}.listen_port="${VPN_PORT}"
    uci add_list network.${VPN_IF}.addresses="${VPN_ADDR}"
    uci add_list network.${VPN_IF}.addresses="${VPN_ADDR6}"
    
    # Add VPN peers
    uci -q delete network.wgclient
    uci set network.wgclient="wireguard_${VPN_IF}"
    uci set network.wgclient.public_key="${VPN_PUB}"
    uci set network.wgclient.preshared_key="${VPN_PSK}"
    uci add_list network.wgclient.allowed_ips="${VPN_ADDR%.*}.2/32"
    uci add_list network.wgclient.allowed_ips="${VPN_ADDR6%:*}:2/128"
    uci commit network
    /etc/init.d/network restart
    ```
    These can also be set from the router interface by going to `Network -> Interface -> Add new interface...` and filling in the fields by hand.

    Server setup is now done. We can move on to the client setup

## Client Setup

1.  Make sure to have to also update and install wireguard according to step 1 of the Server setup

2.  Find the server ip address of your router. If your router is already at another location. Get the internet IP-Address. If you have connected the router locally you can just use the designated IP-Address from earlier for example I use `192.168.3.1` , but note that 
    you have to change this later\
    In the command below this IP-address is referred as `SERVER_ADDRESS`.\
    __TIP:__ If your server router is attached to the same network as your Home-Assistant installation and you use DuckDNS as an URL you can also use that address. If your IP-address ever changes you only have to update your DuckDNS server and reboot your router.
    
    ```bash
    VPN_IF="vpn"
    VPN_SERV="SERVER_ADDRESS"
    VPN_PORT="51820"
    VPN_ADDR="192.168.9.2/24"
    VPN_ADDR6="fd00:9::2/64"
    ```
3.  Here we are going to generate some new keys and add the `Pre-Shared key` and `Public key` we obtained earlier. This differs a bit from the OpenWRT client guide since they presume that the keys are not yes generated\
    Generate a private and public keypair for the client and put the previous stored pre-shared and public-key into their own files. Note that the key needs to be between the quotation marks `""`.
    ```bash
    umask go=
    wg genkey | tee wgclient.key | wg pubkey > wgclient.pub
    echo "PRE_SHARED KEY"    | tee wgclient.psk
    echo "SERVER PUBLIC KEY" | tee wgserver.pub
 
    # Client private key
    VPN_KEY="$(cat wgclient.key)"
 
    # Pre-shared key
    VPN_PSK="$(cat wgclient.psk)"
 
    # Server public key
    VPN_PUB="$(cat wgserver.pub)"
    ```
4.  Next we are going to generate the firewall rules
    ```bash
    # Configure firewall
    uci rename firewall.@zone[0]="lan"
    uci rename firewall.@zone[1]="wan"
    uci del_list firewall.wan.network="${VPN_IF}"
    uci add_list firewall.wan.network="${VPN_IF}"
    uci commit firewall
    /etc/init.d/firewall restart
    ```
    These can also be set from the router interface by going to `Network -> Firewall -> Add` and filling in the fields by hand.

5.  Finally we establish the connection
    ```bash
    # Configure network
    uci -q delete network.${VPN_IF}
    ci set network.${VPN_IF}="interface"
    uci set network.${VPN_IF}.proto="wireguard"
    uci set network.${VPN_IF}.private_key="${VPN_KEY}"
    uci add_list network.${VPN_IF}.addresses="${VPN_ADDR}"
    uci add_list network.${VPN_IF}.addresses="${VPN_ADDR6}"
 
    # Add VPN peers
    uci -q delete network.wgserver
    uci set network.wgserver="wireguard_${VPN_IF}"
    uci set network.wgserver.public_key="${VPN_PUB}"
    uci set network.wgserver.preshared_key="${VPN_PSK}"
    uci set network.wgserver.endpoint_host="${VPN_SERV}"
    uci set network.wgserver.endpoint_port="${VPN_PORT}"
    uci set network.wgserver.route_allowed_ips="1"
    uci set network.wgserver.persistent_keepalive="25"
    ```
    Note these next commands give access to **ALL** ip's from the client side and route all traffic through it. If we dont want that use the other option replace the IP-Address by the local IP-Adresses from the server for example `192.168.1.0/24`
    ```bash
    uci add_list network.wgserver.allowed_ips="0.0.0.0/0"
    uci add_list network.wgserver.allowed_ips="::/0"
    uci commit network
    /etc/init.d/network restart
    ```
6.  Go back to the Server router and add the Allowed IP's in the interface by going to `Network -> Interfaces -> VPN -> Edit -> Allowed IPs`\
    Enter the Local IP-Address range for the client router for me that is `192.168.3.0/24`

    You Now should have a connection. Test this by trying to go the routers page or by pinging a device that is on the other side of the connection.
# Step 3 - Setup Zigbee Networks
This part is fairly straightforward since the networks are now joined almost as a single network and IP-Addresses are easily reachable from both side.

On the side were Home-Assistant is active install the Conbee II stick into deconz. The next steps are for a Home-Assistant installation on a Raspberry Pi(4)
1. Insert the Conbee II stick into a usb-port
2. Install the deCONZ add on from the add on store
3. Select the Conbee II stick. In the Add on configuration
4. Go to the deCONZ intergration and setup a username an password for the stick
5. Now you can add Zigbee Devices

For the side of your client
1. Connect the Zigbee Gateway to your Wifi or Ethernet.
2. Set the IP-Address static. You can easily do this in the OpenWRT interface. By going to the home page and look for the gateway and click `set static`
3. Note the IP-Address the gateway has
4. Go to Home-Assistant and go to `Settings -> Devices & Services -> Add integration`
5. Select `Zigbee Home Automation`\
The next step depends on the Zigbee gateway you have bought. For me it was the following settings
6. `Serial Device Path` is `Enter Manually`
7. `Radio Type` is `EZSP`
8. `Serial device path` is `socket://IP_ADDRESS_OF_GATEWAY:8888` which for me specifically is `socket://192.168.3.2:8888`
9. `port speed` is `57600`

Now you can connect your Zigbee devices as if it was locally installed. Just choose deCONZ or ZHA.