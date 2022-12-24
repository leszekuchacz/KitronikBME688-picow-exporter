# KitronikBME688-picow-exporter

Prometheus exporter to exponse metrics like temperature, pressure, humidity, AirQualityScore and eCo2 from KitronikBME688 + Raspberry pico W. 


## Requirement 

Name     | Description | Cost
---------|-------------|----
KitronikBME688 |  | 
Power Supply 5VAC or usb | *on usb the zled dosent works |
Raspberry pico W | | 

## Installation

1. 

## Use Case
1. Integration with [Rasbeery pi 4 with grove pi stack](https://github.com/leszekuchacz/prometheus-on-raspberrypi-for-grovepi)
![Diagram](https://raw.githubusercontent.com/leszekuchacz/KitronikBME688-picow-exporter/main/docs/prometheus%2Bgrafana-three-KitronikBME688.drawio.png)
## Troubleshooting 

### Raspberry Pico W dosent respond.
1. Turn off power, plug off usb
2. Push bootsel button and plugin in usb cable or turn on power supply.
3. After that should in your system raspberry storage appear. Upload here flash_nuke.uf2(Link)
4. Raspberry will restart. Now repeat intallation steps 1.... 
