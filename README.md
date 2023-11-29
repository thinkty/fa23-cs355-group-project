

## Modules Used

`cryptography`, `socketserver`, `argparse`, `hashlib`

## Protocol

### Assumptions

Bob is able to obtain Alice’s public key. Bob and Alice do not have access to other segments that they don’t have.

### Security Goal

If the RSA assumption holds, and H is an irreversible hash function that is modeled as a random function mapping onto ℤ*N, then RSA-FDH is secure (lecture 14 slide 29) s.t. the adversary should not be able to forge a valid signature on any message not authenticated by the sender. Alice and Bob should only be able to learn the number of overlaps, and the contents of the overlapping segment. This signature scheme is secure as the third party adversary can only forge a valid signature for any message with negligible probability since we use the RSA-FDH signature scheme on top of an additional step of hashing. Assuming that the hash function is a collision resistant random oracle, hashing the digest of the same hash function is collision resistant (lecture 9 slide 9). Therefore, if the RSA assumption holds and the hash function is collision resistant and irreversible, the RSA-FDH signature scheme with an additional hash step is secure. When Alice sends her hashed segments to Bob, Bob is not able to learn the contents of Alice’s segments given that Bob does not have access to all the segments. In a realistic scenario, the company would have an access policy to control who has permission to which segments. Therefore, Bob will not be able to learn about the segments that do not match since the hash function is irreversible.

### Signature Scheme

- (N, e, d, h1, h2, h3, h4, h5) <- Gen(1<sup>n</sup>) : Generate the RSA public keys and private key for the digital signature, and also the hash of the 5 segments.
- (h, σ) <- Sign<sub>sk</sub>(h) : The signature takes as input the digest of the segment and the secret key and signs the digest as follows:
1. h' = H(h)
2. σ = h’<sup>d</sup> mod N
- {1,0} <- Vrfy(h, σ) : The verification takes as input the digest and the signature and verifies the signature as follows:
1. h' = H(h)
2. Return 1 iff σ<sup>e</sup> == h’ mod N

### Third Party Adversary Goal

Forge a valid signature for any message with non-negligible probability.

## Protocol In Use

1. Alice first starts the server via `python alice.py [Alice's segment files]`.
2. Bob starts the client via `python bob.py [Bob's segment files]`
3. Bob's client application returns the number of matches.