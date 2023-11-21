
import socket

if __name__ == "__main__":
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 55555))

    # TODO: compute digest of the segments

    # TODO: request alice with a specific segment number

    message = 'hello'
    print("bob > {}".format(message))
    clientsocket.send(message.encode('utf-8'))
    data = clientsocket.recv(1024)
    text = data.decode('utf-8')
    print("bob < {}".format(text))