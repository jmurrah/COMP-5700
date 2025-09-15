PRINCIPLES = {
    "NO_CUSTOM_CRYPTO": {
        "name": "Do not use your own cryptographic algorithms or implementations",
        "purpose": "Custom implementations are risky and not peer-reviewed.",
        "violations": [
            "This requirement involves implementing our own cryptographic algorithm.",
            "This requirement uses a custom implementation of a cryptographic function.",
            "This requirement develops an in-house cryptographic solution.",
            "This requirement creates a proprietary cryptographic implementation.",
            "This requirement implements our own version of an existing algorithm.",
        ],
        "compliance": [
            "This requirement uses vetted, industry-standard crypto libraries.",
            "This requirement relies on established cryptographic libraries."
        ],
    },
    "PROPER_LIBRARY_USE": {
        "name": "Misuse of libraries and algorithms",
        "purpose": "Wrong primitives/params or deprecated algos compromise security.",
        "violations": [
            "This requirement uses MD5 for password encryption.",
            "This requirement uses MD5 for encrypting sensitive data.",
            "This requirement uses SHA1 for security-critical operations.",
            "This requirement uses DES or 3DES encryption.",
            "This requirement uses RC4 for encryption.",
            "This requirement uses a deprecated cryptographic algorithm.",
            "This requirement uses MD5 for password hashing.",
            "This requirement uses fast hashing algorithms for passwords.",
            "This requirement chooses weak cryptographic primitives.",
            "This requirement uses outdated encryption methods.",
        ],
        "compliance": [
            "This requirement uses modern, secure cryptographic algorithms.",
            "This requirement specifies recommended cryptographic primitives.",
            "This requirement uses strong hashing algorithms like bcrypt or Argon2.",
            "This requirement chooses secure cryptographic libraries."
        ],
    },
    "PROPER_KEY_MANAGEMENT": {
        "name": "Poor key management",
        "purpose": "Keys must be generated, stored, rotated, and destroyed properly.",
        "violations": [
            "This requirement hardcodes cryptographic keys.",
            "This requirement stores keys in source code.",
            "This requirement lacks key rotation mechanisms.",
            "This requirement does not specify key lifecycle management.",
            "This requirement uses static keys without rotation.",
            "This requirement embeds secrets in configuration files.",
        ],
        "compliance": [
            "This requirement implements key rotation.",
            "This requirement rotates cryptographic keys regularly.",
            "This requirement rotates keys for the vault.",
            "This requirement manages key lifecycle properly.",
            "This requirement uses secure key storage mechanisms.",
        ],
    },
    "TRUE_RANDOMNESS": {
        "name": "Randomness that is not random",
        "purpose": "Crypto needs unpredictable, CSPRNG-grade randomness.",
        "violations": [
            "This requirement uses a fixed range for random number generation.",
            "This requirement uses predictable randomness.",
            "This requirement generates random numbers in a limited range.",
            "This requirement uses deterministic random number generation.",
            "This requirement uses non-cryptographic random number generators.",
            "This requirement constrains randomness to specific values.",
            "This requirement generates numbers between fixed values.",
        ],
        "compliance": [
            "This requirement uses cryptographically secure random number generation.",
            "This requirement uses unpredictable randomness.",
            "This requirement employs secure random number generators.",
        ],
    },
    "ALGORITHM_ADAPTABILITY": {
        "name": "Failure to allow for algorithm adaptation and evolution",
        "purpose": "Systems must support crypto agility.",
        "violations": [
            "This requirement hardcodes the cryptographic algorithm permanently.",
            "This requirement provides no mechanism to upgrade algorithms.",
            "This requirement locks in a specific algorithm without flexibility.",
            "This requirement cannot adapt to new cryptographic standards.",
        ],
        "compliance": [
            "This requirement supports upgrading to stronger algorithms.",
            "This requirement enables cryptographic agility.",
            "This requirement allows algorithm evolution and adaptation.",
            "This requirement supports future algorithm upgrades.",
            "This requirement can adapt to new cryptographic methods.",
            "This requirement allows switching to better cryptographic algorithms.",
            "This requirement enables upgrading to stronger cryptography when available.",
        ],
    },
}