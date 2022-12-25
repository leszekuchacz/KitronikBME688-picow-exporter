# KitronikBME688-picow-exporter

Prometheus exporter to exponse metrics like temperature, pressure, humidity, AirQualityScore and eCo2 from KitronikBME688 + Raspberry pico W. 


## Requirement 

Name     | Description | Cost| Link|
---------|-------------|------------
Air Quality Datalogging Board - Kitronik 5336 - BME688| 55$  | Complete air monitoring and reporting solution for the Raspberry Pi Pico |https://kitronik.co.uk/blogs/resources/pico-smart-air-quality-board-using-the-bme688-sensor|
Power Supply 5VAC or usb | *on usb the zled dosent works | 10$ | |
Raspberry pico W | |10$ | |

## Installation
*if this your first run with pico w, you need to do this first https://projects.raspberrypi.org/en/projects/get-started-pico-w

1. Install raspverry pi pico w to Kitronik.
2. Upload this project files by Thonny program.
3. Run main.py. 

## Use Case
1. Integration with [Rasbeery pi 4 with grove pi stack](https://github.com/leszekuchacz/prometheus-on-raspberrypi-for-grovepi)
![Diagram](https://raw.githubusercontent.com/leszekuchacz/KitronikBME688-picow-exporter/main/docs/prometheus%2Bgrafana-three-KitronikBME688.drawio.png)
## Troubleshooting 

### Raspberry Pico W dosent respond.
1. Turn off power, plug off usb
2. Push bootsel button and plugin in usb cable or turn on power supply.
3. After that should in your system raspberry storage appear. Upload here flash_nuke.uf2(Link)
4. Raspberry will restart. Now repeat intallation steps 1.... 
