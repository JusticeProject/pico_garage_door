from machine import Pin
import network
import usocket as socket
import secrets
import time

# from https://toptechboy.com/sending-data-over-wifi-between-raspberry-pi-pico-w-and-your-pc/

# status LED
led = Pin("LED", Pin.OUT)
led.on()

network.country("US") # or import rp2  then rp2.country("US")
network.hostname("picow")
wlan = network.WLAN(network.STA_IF)
print("wlan created")
wlan.active(True)
print("wlan active")
wlan.connect(secrets.SSID, secrets.PASSWORD)
print("connecting")
 
# Wait for connection
while not wlan.isconnected():
    time.sleep(1)
    print("waiting...")
print('WiFi connected')
print(wlan.ifconfig())
 
# Set up UDP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((wlan.ifconfig()[0], 12345))
print("Server is Up and Listening")
print(wlan.ifconfig()[0])

led.off()

try:
    while True:
        print('Waiting for a request from the client...')
        request, client_address = server_socket.recvfrom(1024)
        print("Client Request:",request.decode())
        print("FROM CLIENT",client_address)
        
        # String to send
        data = "225,128,64"
        
        # Send data to client
        server_socket.sendto(data.encode(), client_address)
        print(f'Sent data to {client_address}')
        
        # Optional: Pause for a short period to prevent overwhelming the client
        time.sleep(1)
except KeyboardInterrupt:
    print("interrupted")
    wlan.disconnect()
