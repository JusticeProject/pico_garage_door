import socket

server_addr_port = socket.getaddrinfo("picow.local", 12345)[0][-1]
print(server_addr_port)

# Set up UDP client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
# Send request to the server
client_socket.sendto(b"Knock", server_addr_port)

# Receive data from the server
data, addr = client_socket.recvfrom(1024)
print(f"Received {len(data)} bytes")
