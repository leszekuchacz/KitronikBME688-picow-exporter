from PicoAirQuality import KitronikBME688, KitronikOLED, KitronikRTC, KitronikButton, KitronikBuzzer, KitronikZIPLEDs
import time,network,socket, machine, _thread, utime
import config
import urequests,ujson

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
    print("Binding socket on "+config.webserver_host+" port "+str(config.webserver_port))
    address = (config.webserver_host, config.webserver_port)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webserver(connection):
    global reset_timer
    while True:
        print("Waiting for connection")
        client,addr = connection.accept()
        print("Connection accept from", addr)
        
        #print(utime.ticks_diff(start,utime.ticks_us()))
        
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
        print("Close connection from", addr)
        client.close()
        reset_timer=0
    
        
        

def oled_display(timer):
    if config.oled is True:
        oled.poweron()
        if (timer>=10 and timer<=25 or timer>=45 and timer<=58 or timer>=75 and timer<=85 or  timer>=100 and timer<=115):
            oled.clear()
            oled.drawRect(4, 5, 120, 35)
            oled.displayText(rtc.readDateString(), 2, 25)
            oled.displayText(rtc.readTimeString(), 3, 33)
            oled.show()
        else:    
            bme688.measureData()

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
        oled_display(reset_timer)
        buttons.buttonA.irq(trigger=machine.Pin.IRQ_RISING, handler=ButtonA_IRQHandler)
        buttons.buttonB.irq(trigger=machine.Pin.IRQ_RISING, handler=ButtonB_IRQHandler)
        utime.sleep(1)
        threadlock.release()
        #print(reset_timer)
        if config.webserver_heartbeat!=0 and reset_timer>=config.webserver_heartbeat:
            print("reset_timer: "+str(reset_timer)+" webserver_heartbeat: "+str(config.webserver_heartbeat))
            print("Reset machine due to exceeding webserver_heartbeat time")
            machine.reset()
            

reset_timer = 0
def interruption_handler(pin):
    global reset_timer
    reset_timer += 1 

def sync_time_via_http():
    # expecting this json body in request {"datetime":"2023-04-20T19:00:21.664729+02:00"}
    req=urequests.get(config.rtctime_sync_http_url)
    date=req.json()
    print(date['datetime'])
    date1=date['datetime'].rsplit('-',2)
    date2=date1[2].rsplit('T',2)
    date3=date2[1].rsplit(':',4)
    date4=date3[2].rsplit('.',2)

    year=int(date1[0])
    month=int(date1[1])
    day=int(date2[0])
    hour=int(date3[0])
    minute=int(date3[1])
    second=int(date4[0])

    rtc.setDate(int(day), int(month),int(year))
    rtc.setTime(int(hour), int(minute), int(second))
    print("Sync_time_via_http done.")
    req.close()

###   MAIN   ###
soft_timer = machine.Timer(mode=machine.Timer.PERIODIC, period=1000, callback=interruption_handler)      


print("Starting setup BME688.")
bme688 = KitronikBME688()
oled = KitronikOLED()
rtc = KitronikRTC()
buzzer = KitronikBuzzer()
buttons = KitronikButton()
zipleds = KitronikZIPLEDs(3)
print("Starting KitronikBME688 Gas Sensor.")
bme688.setupGasSensor()
print("Starting KitronikBME688 Baseline.")
bme688.calcBaselines()
print("Starting wifi.")
wifi()
print("Starting sync time via http api.")
time.sleep(1)
sync_time_via_http()
# todo alarm 
#rtc.setAlarm(14, 1)

##
connection=open_socket()
print("Starting input thread")
# picow W has 2 cores, first is used for connect waiting(webserver), second for input waiting(second_thred)
_thread.start_new_thread(thread_second, ())
print("Starting webserver")
webserver(connection)




