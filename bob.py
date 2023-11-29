
import argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import socket
import hashlib

server_addr = 'localhost'
server_port = 55555

def connectAndRequest(segnum: int) -> str:
    # Connect to alice
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((server_addr, server_port))

    # Send the request
    clientsocket.send(str(segnum).encode('utf-8'))

    # Receive public key, message, and signature
    message = clientsocket.recv(65) # 1 byte of segnum, 32 bytes (256 bits) of digest (but x2 since hex)
    signature = clientsocket.recv(256) # signature of 2048 bit key size has 256 (2048 bits) bytes
    clientsocket.close()

    # Open Alice's public key (We assume that the public key is shared with Bob safely)
    with open('alice_public_key.pem', 'rb') as public_key_file:
        public_key_bytes = public_key_file.read()
    public_key = serialization.load_pem_public_key(public_key_bytes, default_backend())

    # Verify assuming that the adversary cannot modify public key
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return message.decode('utf-8')
    except Exception as e:
        print('error: {}'.format(e))
        return ''

if __name__ == "__main__":

    # Parse the segment names
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='segments', type=str, nargs='+', help='File name of 5 segments')
    args = parser.parse_args()
    segments = args.files
    if len(segments) != 5:
        print('error: must specify 5 segment files...')
        exit(1)

    # Compute digest of the segments
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

    # Make a request for each segment and compare
    matches = 0
    for segnum in range(5):
        print('Requesting segment {}'.format(segnum))
        message = connectAndRequest(segnum)
        if message == '':
            print('error: failed to verify received message...')
            exit(1)

        # Check that the requested segnum is the same as received
        if segnum != int(message[:1]):
            print('error: different segnum received...')
            exit(1)

        # Check if there is a match with the received digest
        digest = message[1:]
        for i in range(5):
            if digests[i] == digest:
                matches += 1
                break
    
    print('Matches found: {}'.format(matches))