
from cryptography.hazmat.primitives.asymmetric import rsa
import socketserver
import sys

class SignatureRequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request.recv(1024)
        text = data.decode('utf-8')

        # TODO: request should be a number indicating the segment number (make sure the segment number is in bound)

        # TODO: sign the requested segment's digest and send public keys with it

        print("alice < {}".format(text))
        self.request.send('OK'.encode('utf-8'))
        self.request.close()

class SignatureServer(socketserver.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate: bool = True) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

if __name__ == "__main__":
    
    # TODO: generate RSA key pair

    # TODO: compute digest of each segment 

    server = SignatureServer(('localhost', 55555), SignatureRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit()