## Again we import the necessary socket python module
import socket

## Here we define the UDP IP address as well as the port number that we have
## already defined in the client python script.
# The ipAdress if of this host MAchine - Input the samr adres and port in the simulator settings
UDP_IP_ADDRESS = "157.82.160.46"
UDP_PORT_NO = 4001

## declare our serverSocket upon which
## we will be listening for UDP messages
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

## One difference is that we will have to bind our declared IP address
## and port number to our newly declared serverSock
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

print("server online!")

while True:
    data, addr = serverSock.recvfrom(1024)
    data_list = list(data)
    
    print (f"Raw Data: {data}")    
    # print (f"List: {data_list}")