
import argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import hashlib
import socketserver
import sys

responses = []
public_key_pem = None

class SignatureRequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request.recv(1024)
        segnum = int(data.decode('utf-8'))

        # Get segment number from the request (between 0 and 4)
        if segnum < 0 or segnum > 4 or public_key_pem is None or len(responses) != 5:
            self.request.send('ERR'.encode('utf-8'))
            self.request.close()
            return

        # Send the public key, message, and signature
        print("Sending segment {}".format(segnum))
        self.request.sendall(public_key_pem + responses[segnum][0] + responses[segnum][1])
        self.request.close()

class SignatureServer(socketserver.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate: bool = True) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

if __name__ == "__main__":

    # Parse the segment names
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='segments', type=str, nargs='+', help='File name of 5 segments')
    args = parser.parse_args()
    segments = args.files
    if len(segments) != 5:
        print('error: must specify 5 segment files...')
        exit(1)

    # Compute digest of each segment
    digests = []
    for name in segments:
        try:
            sha256 = hashlib.sha256()
            with open(name, 'rb') as segment:
                for chunk in iter(lambda: segment.read(4096), b''):
                    sha256.update(chunk)
            digests.append(sha256.hexdigest())
        except FileNotFoundError:
            print('error: segment {} not found...'.format(name))
            exit(1)
        except Exception as e:
            print('error: {}'.format(e))
            exit(1)
    print('Digest of segments:')
    for i, digest in enumerate(digests):
        print('{}: {}'.format(i, digest))

    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Serialize the public key into PEM format to be sent to any requester
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Sign each segment and create responses in advance
    for i, segment_digest in enumerate(digests):
        # Prepend the segment index so that if the adversary changes Bob's request, Bob will know
        message = (str(i) + segment_digest).encode('utf-8')
        # Signing will pad the message if necessary and hash the padded message again before signing
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        responses.append((message, signature))

    server = SignatureServer(('localhost', 55555), SignatureRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit()