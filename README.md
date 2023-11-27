

## Dependencies

`cryptography`, `socketserver`, `argparse`, `hashlib`

## Protocol

### Assumptions

Bob is able to obtain Alice’s public key. Bob and Alice do not have access to other segments that they don’t have.

### Security Goal

If the RSA assumption holds, and H is a irreversible hash function that is modeled as a random function mapping onto ℤ*N, then RSA-FDH is secure s.t. the adversary should not be able to forge a valid signature on any message not authenticated by the sender. Alice and Bob should only be able to learn the number of overlaps, and the contents of the overlapping segment.

### Signature Scheme

- (N, e, d, h1, h2, h3, h4, h5) <- Gen(1<sup>n</sup>) : Generate the RSA public keys and private key for the digital signature, and also the hash of the 5 segments.
- (h, σ) <- Sign<sub>sk</sub>(h) : The signature takes as input the digest of the segment and the secret key and signs the digest as follows:
1. h' = H(h)
2. σ = h’<sup>d</sup> mod N
- {1,0} <- Vrfy(h, σ) : The verification takes as input the digest and the signature and verifies the signature as follows:
1. h' = H(h)
2. Return 1 iff σ<sup>e</sup> == h’ mod N

### Adversary Goal

Forge a valid signature for any message with non-negligible probability.
