from PicoAirQuality import KitronikBME688, KitronikOLED, KitronikRTC, KitronikButton, KitronikBuzzer, KitronikZIPLEDs
import time,network,socket, machine, _thread, utime
import config

def wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.wifi_ssid, config.wifi_password)
    #define CYW43_LINK_UP           (3)     ///< Connect to wifi with an IP address
    max_wait = config.wifi_timeout
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3: 
            print("Wifi has connected "+wlan.ifconfig()[0])
            break
        max_wait -= 1
        print('waiting for wifi connection...')
        time.sleep(1)
    if  wlan.isconnected() == False:
        machine.reset()
    else:
        return wlan.ifconfig()[0]

def open_socket():
    # Open a socket
    print("Binding socket on "+config.host+" port "+str(config.port))
    address = (config.host, config.port)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webserver(connection):
    while True:
        print("Waiting for connection")
        client,addr = connection.accept()
        print("Connection accept from", addr)
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
            print(request)
        except IndexError:
            pass
        t = "# HELP bmi688_temperature celusish\n# TYPE bmi688_temperature gauge\nbmi688_temperature "+str(bme688.readTemperature())
        p = "# HELP bmi688_pressure Pa\n# TYPE bmi688_pressure gauge\nbmi688_pressure "+str(bme688.readPressure())
        h = "# HELP bmi688_humidity %\n# TYPE bmi688_humidity gauge\nbmi688_humidity "+str(bme688.readHumidity())
        a = "# TYPE bmi688_airqualityscore gauge\nbmi688_airqualityscore "+str(bme688.getAirQualityScore())
        c = "# HELP bmi688_eco2 ppm\n# TYPE bmi688_eco2 gauge\nbmi688_eco2 "+str(bme688.readeCO2())
        html=t+"\n"+p+"\n"+h+"\n"+a+"\n"+c
        client.send("HTTP/1.0 200 OK\r\nContent-type: text/plain; version=0.0.4; charset=utf-8\r\n\r\n")
        client.send(html)
        client.close()
        print("Close connection from", addr)

def oled_display():
    if config.oled is True:
        bme688.measureData()
        oled.poweron()
        oled.clear()
        oled.displayText("Temp: " + str(bme688.readTemperature()) + " C", 1)
        oled.displayText("Pres: " + str(bme688.readPressure()) + " Pa", 2)
        oled.displayText("Hum: " + str(bme688.readHumidity()) + " %", 3)
        oled.displayText("IAQ: " + str(bme688.getAirQualityScore()), 4)
        oled.displayText("eCO2: " + str(bme688.readeCO2()) + " ppm", 5)
        oled.show()
    else:
        oled.poweroff()
        
def zipleds_color(on,red,green,blue):
    if on == True:
        print("zipleds show")
        zipleds.setBrightness(100)
        zipleds.setLED(0, (red, green, blue))
        zipleds.setLED(1, (red, green, blue))
        zipleds.setLED(2, (red, green, blue))
        zipleds.show()
    else:
        print("zipleds clear")
        zipleds.clear(0)
        zipleds.clear(1)
        zipleds.clear(2)
ButtonAcounter=0
ButtonBcounter=0
def ButtonA_IRQHandler(pin):
    global ButtonAcounter
    ButtonAcounter+=1
    print("Button A was pressed for "+str(ButtonAcounter))
    zipleds_color(True,255,0,0)
    buzzer.playTone_Length(1000, 2000)
    config.oled=True
    zipleds_color(False,255,0,0)
    
def ButtonB_IRQHandler(pin):
    global ButtonBcounter
    ButtonBcounter+=1
    print("Button B was pressed for "+str(ButtonBcounter))
    buzzer.playTone_Length(1000, 2000)
    config.oled=False


threadlock = _thread.allocate_lock()
def thread_second():
    while True:
        threadlock.acquire()
        oled_display()
        buttons.buttonA.irq(trigger=machine.Pin.IRQ_RISING, handler=ButtonA_IRQHandler)
        buttons.buttonB.irq(trigger=machine.Pin.IRQ_RISING, handler=ButtonB_IRQHandler)
        utime.sleep(1)
        threadlock.release()

###   MAIN   ###
print("Starting setup BME688")
bme688 = KitronikBME688()
oled = KitronikOLED()
rtc = KitronikRTC()
buzzer = KitronikBuzzer()
buttons = KitronikButton()
zipleds = KitronikZIPLEDs(3)
# todo get time from ntp
#rtc.setDate(19, 12, 2022)
#rtc.setTime(01, 20, 00)
#rtc.setAlarm(14, 1)
print("Setup KitronikBME688 Gas Sensor")
bme688.setupGasSensor()
print("Setting KitronikBME688 Baseline.")
bme688.calcBaselines()
wifi()
connection=open_socket()
print("Starting input thread")
# picow W has 2 cores, first is used for connect waiting(webserver), second for input waiting(second_thred)
_thread.start_new_thread(thread_second, ())
print("Starting webserver")
webserver(connection)



