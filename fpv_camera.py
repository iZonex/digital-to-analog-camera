import pigpio
import time
import requests

GPIO_PIN = 18
NEUTRAL_LOW = 1480
NEUTRAL_HIGH = 1520

pi = pigpio.pi()
if not pi.connected:
    exit("Can't connect to pigpio daemon. Is pigpiod running?")

def send_request(command):
    url = 'http://192.168.133.208/setPTZCmd'
    headers = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-type': 'application/x-www-form-urlencoded',
        'Cookie': 'DHLangCookie30=English; ipc_192.168.133.208_webLanguage=en_us; ipc_192.168.133.208_KeepScale=0; ipc_192.168.133.208_username=admin; ipc_192.168.133.208_password=E10ADC3949BA59ABBE56E057F20F883E',
        'Origin': 'http://192.168.133.208',
        'Referer': 'http://192.168.133.208/',
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = f'<?xml version="1.0"?><soap:Envelope xmlns:soap="http://www.w3.org/2001/12/soap-envelope"><soap:Header><userid>52851dbd7918bbae</userid><passwd>a17faccd02661e4c</passwd></soap:Header><soap:Body><xml><cmd>{command}</cmd></xml></soap:Body></soap:Envelope>'
    requests.post(url, headers=headers, data=data, verify=False)
    print(f"Command sent: {command}")

def monitor_pwm(gpio, level, tick):
    global last_command
    if level == 1:
        monitor_pwm.start_tick = tick
    elif level == 0 and monitor_pwm.start_tick is not None:
        pulse_width = pigpio.tickDiff(monitor_pwm.start_tick, tick)
        if NEUTRAL_LOW <= pulse_width <= NEUTRAL_HIGH:
            if last_command != "neutral":
                send_request("stop")
                last_command = "neutral"
        elif pulse_width > NEUTRAL_HIGH and last_command != "in":
            send_request("zoomtele")
            last_command = "in"
        elif pulse_width < NEUTRAL_LOW and last_command != "out":
            send_request("zoomwide")
            last_command = "out"

monitor_pwm.start_tick = None
last_command = "neutral"


pi.set_mode(GPIO_PIN, pigpio.INPUT)
callback = pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, monitor_pwm)

try:
    print("Monitoring PWM. Press CTRL+C to exit.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    callback.cancel()
    pi.stop()
