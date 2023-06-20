# Connecting long range sensors using LoRa and MQTT

This post is written as part of an assignment for the HAN University of Applied Sciences. This is also part of a few other projects I am posting.
Other guides can be found here:\
Two Zigbee Networks Joined over a wireguard VPN: `TBD`\
Controlling Tuya devices locally using Node-Red:`TBD`

This guide presumes that you have some basic knowledge of using Home-Assistant and that Home-Assistant is already installed. I am not liable for broken devices, broken configuration, thermonuclear war or ANYTHING ELSE. This guide is provided as is. Nonetheless I hope you find it interesting :D

# Introduction
Unlike the other posts I made. This isn't a guide but more of an exploration of what is possible. At this point with my Home-Assistant installation I could add Zigbee devices and Wi-Fi devices and sensors at my own studio and at my parents place which is connected through a VPN. However I couldn't put sensors in the yard of my parents or put a device at a long-range without an internet connection or Zigbee Signal from either gateways.\
That is why I decided to explore with a Point to Point LoRa connection. I Have used used LoRaWAN with The Things Network, but neither my parents place or my own studio have very good coverage of TTN. So I bought to ESP32 modules with a SX1276 Lora chip and went coding.

## Goal of this project
The point of using LoRa is to get a longer range. So I wanted to see how far I could get in a semi urban area with some lower power modules.

# Modules
I opted to buy two LilyGO TTGO T3 LoRa32 V1.6.1 ESP32 Modules. With some cheap antenna's from amazon not for extended range but more for antenna placement.\
<img src="./pics/LILYGO-G511-01_1_-600x600.jpeg" alt="LilyGO TTGO T3 LoRa32 V1.6.1 ESP32 Module" width="20%" height ="20%">

# The Project
A few years ago I made a small joke project in where a traffic light was hooked up to fridge. When the fridge would open the traffic light would go to green and cycle back through orange and eventually to Red.
This was controlled by Arduino Nano which which would constantly read a digital pin to check if the fridge light was activated. If the fridge light turned on the pin would go high and the light would turn green.

## Hardware
The Hardware consist of Node and Gateway.

### The Node
The Board that controlled the traffic light becomes the node and originally looked like this:

<img src="./pics/PXL_20230611_142327017.png" alt="Original board" width="20%" height ="20%">

There are two relays to switch live and neutral wires per light so six relays in total. The Red light has inverted logic because that is light that is almost always on since the fridge is closed most of the time and no relays are active.
The relays are controlled using BJT transistors and there debugging LED's on the board for programming the board if it is removed from the traffic light.

This meant that the board was almost ready only the pins for had to be mapped to appropriate pins on the LilyGo.\
The pinout for this was changed as follows:

| **Function**          | **Arduino Nano Pin**       | **LilyGO Pin**    |
|-                      |-                           |-                  |
| Green light           | D11                        | GPIO12            |
| Yellow Light          | D5                         | GPIO13            |
| Red light (inverted)  | D2                         | GPIO15            | 
| Fridge Read Pin       | A2                         | GPIO2             |

After some more soldering with protoboard it looked like this:\
<img src="./pics/PXL_20230611_192514070.png" alt="Adjusted board" width="20%" height ="20%">

### The Gateway
The Gateway is just the LilyGo module described earlier that is connected to a Wifi Network.
The Node and Gateway are about 1 km apart from each other. The Gateways job is to translate MQTT message into LoRa messages.
# Software Design
There are two pieces of different software written. The Node is in control of traffic light and The Gateway is in control of processing MQTT messages and sending them over LoRa.
## The Node
The Node can control the traffic light in three Modes: Manual, Automatic and Flicker
### Manual
In the manual mode you can select a color from the Home Assistant color wheel. Green controls the green stoplight, red Controls the red stoplight, and blue controls the yellow stoplight.\
The Rreason that blue is controlling the yellow light is so that there is finer control after all and there is no blue light in the traffic light so nothing goes to waist. It also easier to code since each light has its own value from `0` to `255`
However the light are binary. This means that they either on or off. So I mapped that above `200` the light is `on` and below `200` the light is `off`
### Flicker
Flicker is essentially the same as the manual mode only that the light flickers at the selected color with an interval of `1` second.
### Automatic
The Automatic mode is the original function of the traffic light. This means when the fridge is opened it is turning the light green and when it closes it turns the light to orange and then red on an interval of `2` seconds.

### Counting how many times the fridge has opened
Whenever the fridge is opened it stores it in ringbuffer. When the transmit interval occurs for LoRa it sends back a ping that the fridge has opened. This is then turned back into a MQTT message and registered by node red to the a virtual sensor.

# Software implementation
For this to be controlled from Home Assistant I wanted to control it from MQTT. But since I don't really like the normal MQTT Light implementation I opted to use A virtual light in combination with Node-Red. See my guide on controlling Tuya light were I basically did the same thing. But in short I created a fake light with the virtual HACS plugin you can find [here](https://github.com/twrecked/hass-virtual)\
The config looks like this:
```yaml
- platform: virtual
  name: Sociale Leven Stoplicht
  initial_value: "on"
  initial_brightness: 100
  support_color: true
  initial_color: [0, 100]
  support_effect: true
  initial_effect: "Automatic"
  initial_effect_list: ["Automatic", "Flicker", "Manual"]
```
From here I created Node-Red Flow:\
<img src="./pics/Node-RED_Flow.png" alt="Node-RED flow" width="30%" height ="30%">
This flow can be found in my github [here]()


For example if i set it to the mode to manual and choose green as a color it sends the following JSON:
```json
{
   "state":"on",
   "mode":"Manual",
   "red":false,
   "green":true,
   "yellow":false
}
```

