PRINCIPLES = {
    "TRUE_RANDOMNESS": [
        {
            "violation": "Generates 'random' numbers from fixed/small ranges for secrets or nonces.",
            "keywords": [
                "fixed range",
                "between",
                "small range",
                "limited range",
                "from 1 to",
                "range of",
                "bounded",
            ],
        },
        {
            "violation": "Uses non-cryptographic RNGs (e.g., Math.random(), rand()) for keys, IVs, tokens.",
            "keywords": [
                "math.random",
                "rand()",
                "random()",
                "system.random",
                "stdlib random",
                "mersenne twister",
                "linear congruential",
            ],
        },
        {
            "violation": "Reuses or predicts nonces/IVs; seeds PRNGs with predictable values.",
            "keywords": [
                "predictable",
                "reuse",
                "static",
                "constant",
                "same nonce",
                "fixed iv",
                "fixed seed",
            ],
        },
        {
            "violation": "Seeds CSPRNGs with low-entropy inputs (timestamps, PIDs, static seeds).",
            "keywords": [
                "timestamp",
                "time seed",
                "pid",
                "process id",
                "current time",
                "system time",
                "date seed",
            ],
        },
        {
            "violation": "Uses time-based or sequential identifiers (e.g., UUIDv1) as secrets or tokens.",
            "keywords": [
                "uuid1",
                "uuidv1",
                "sequential",
                "incremental",
                "counter",
                "auto increment",
            ],
        },
        {
            "violation": "Overwrites or replaces OS CSPRNG with weaker custom randomness.",
            "keywords": [
                "replace csprng",
                "override random",
                "custom random",
            ],
        },
    ],
    "PROPER_LIBRARY_USE": [
        {
            "violation": "Uses MD5 or SHA-1 for password hashing or digital signatures.",
            "keywords": ["md5", "sha1", "sha-1"],
        },
        {
            "violation": "Uses RC4, DES, or 3DES for encryption.",
            "keywords": [
                "rc4",
                "des",
                "3des",
                "triple des",
                "data encryption standard",
            ],
        },
        {
            "violation": "Stores passwords with reversible encryption instead of a password hashing KDF.",
            "keywords": [
                "password encrypt",
                "encrypt password",
                "reversible password",
                "password cipher",
                "decrypt password",
            ],
        },
        {
            "violation": "Uses fast/general-purpose hashes (e.g., SHA-256) for password storage instead of a password hashing KDF.",
            "keywords": [
                "sha256 password",
                "sha-256 password",
                "sha512 password",
                "password sha",
            ],
        },
        {
            "violation": "Encrypts without authentication (e.g., AES-CBC without a MAC or no tag verification).",
            "keywords": [
                "aes-cbc",
                "cbc mode",
                "no mac",
                "without authentication",
                "no hmac",
            ],
        },
        {
            "violation": "Uses ECB mode for sensitive data.",
            "keywords": ["ecb", "electronic codebook", "aes-ecb"],
        },
        {
            "violation": "Uses predictable or static IVs/nonces with block/stream ciphers.",
            "keywords": [
                "static iv",
                "fixed iv",
                "zero iv",
                "constant nonce",
                "repeated nonce",
            ],
        },
        {
            "violation": "Derives keys directly from passwords without a KDF (PBKDF2, scrypt, bcrypt, Argon2).",
            "keywords": [
                "direct password",
                "password as key",
                "no kdf",
                "no pbkdf",
                "no scrypt",
                "no bcrypt",
            ],
        },
        {
            "violation": "Uses weak key sizes or deprecated curves (e.g., RSA ≤ 1024 bits, legacy/insecure ECC curves).",
            "keywords": ["rsa 1024", "512 bit", "1024 bit", "weak key"],
        },
        {
            "violation": "Accepts self-signed, expired, or hostname-mismatched TLS certificates.",
            "keywords": [
                "self-signed",
                "ignore certificate",
                "skip validation",
                "disable certificate",
                "no certificate check",
            ],
        },
    ],
    "NO_CUSTOM_CRYPTO": [
        {
            "violation": "Reimplements a standard crypto primitive instead of using a proven library.",
            "keywords": ["our own", "implementation"],
        },
        {
            "violation": "Uses a proprietary or in-house cryptographic algorithm.",
            "keywords": [
                "custom",
                "in-house",
                "proprietary",
                "self-made",
                "home-built",
                "roll our own",
            ],
        },
        {
            "violation": "Designs a homegrown key exchange or authentication protocol (DIY TLS/JWT/OAuth).",
            "keywords": [
                "homegrown",
                "diy tls",
                "custom tls",
                "own protocol",
                "custom protocol",
                "handshake",
            ],
        },
        {
            "violation": "Implements a novel cipher, hash, signature, PRNG/DRBG, or protocol.",
            "keywords": [
                "novel cipher",
                "new algorithm",
                "custom cipher",
                "invented",
                "designed",
            ],
        },
        {
            "violation": "Modifies standardized algorithms (e.g., 'our own SHA-512 variant').",
            "keywords": [
                "variant",
                "modified",
                "altered",
                "tweaked",
                "enhanced",
                "improved",
                "custom sha",
                "custom aes",
            ],
        },
        {
            "violation": "Creates a custom padding, MAC, or KDF construction instead of standardized ones.",
            "keywords": ["custom padding", "custom mac", "custom kdf", "own padding"],
        },
        {
            "violation": "Relies on secrecy of the algorithm (security by obscurity) rather than public review.",
            "keywords": [
                "secret algorithm",
                "hidden algorithm",
                "proprietary algorithm",
                "closed source",
            ],
        },
        {
            "violation": "Implements asymmetric crypto (RSA/ECC) from scratch rather than using a vetted library.",
            "keywords": [
                "from scratch",
                "ground up",
                "implement rsa",
                "implement ecc",
                "build rsa",
            ],
        },
        {
            "violation": "Builds a custom stream cipher or block mode instead of standardized AEAD modes.",
            "keywords": ["custom mode", "own cipher", "custom stream"],
        },
    ],
    "PROPER_KEY_MANAGEMENT": [
        {
            "violation": "Hardcodes keys, credentials, or secrets in source or client-side code.",
            "keywords": [
                "hardcode",
                "hard-code",
                "embedded",
                "in source",
                "in code",
                "source code",
                "compiled in",
            ],
        },
        {
            "violation": "Stores keys in plaintext configuration files, environment variables without protection, or logs.",
            "keywords": [
                "plaintext",
                "plain text",
                "clear text",
                "unencrypted",
                "config file",
                "environment variable",
                "env var",
                "log file",
            ],
        },
        {
            "violation": "Commits secrets or keys to version control systems.",
            "keywords": [
                "version control",
                "git commit",
                "repository",
                "commit",
                "checked in",
            ],
        },
        {
            "violation": "Uses shared/static keys across environments, services, or tenants.",
            "keywords": [
                "shared key",
                "static key",
                "global key",
                "same key",
                "reused key",
            ],
        },
        {
            "violation": "Generates keys with insufficient entropy or predictable seeds.",
            "keywords": [
                "low entropy",
                "weak entropy",
                "predictable seed",
                "deterministic key",
            ],
        },
        {
            "violation": "Stores master keys alongside the ciphertext (no key separation or envelope encryption).",
            "keywords": ["key with data", "no separation", "same location"],
        },
        {
            "violation": "Provides no access control, least privilege, or audit trails for key access/usage.",
            "keywords": ["no access control", "full access", "no audit", "no logging"],
        },
        {
            "violation": "Transmits keys over insecure channels or without key wrapping.",
            "keywords": [
                "unencrypted transmission",
                "plain transmission",
                "insecure channel",
                "http",
                "no wrapping",
            ],
        },
        {
            "violation": "Leaves key material in memory longer than necessary or exposes it to crash dumps.",
            "keywords": ["memory dump", "swap file", "core dump", "memory leak"],
        },
    ],
    "ALGORITHM_ADAPTABILITY": [
        {
            "violation": "Hardcodes algorithms or key sizes with no upgrade path.",
            "keywords": [
                "hardcode algorithm",
                "fixed algorithm",
                "static algorithm",
                "no upgrade",
                "no migration",
            ],
        },
        {
            "violation": "Lacks a policy/process to track deprecations and rotate to compliant options.",
            "keywords": ["no policy", "no process", "no deprecation", "no tracking"],
        },
        {
            "violation": "Pins to deprecated algorithms despite available alternatives.",
            "keywords": ["pinned", "locked", "stuck", "cannot change", "fixed version"],
        },
        {
            "violation": "Cannot switch algorithms, modes, or parameters via configuration or policy.",
            "keywords": ["no configuration", "not configurable", "hardwired"],
        },
        {
            "violation": "Lacks migration playbooks for retiring weak algorithms and re-encrypting data at rest.",
            "keywords": ["no migration plan", "no playbook", "no re-encryption"],
        },
        {
            "violation": "Does not monitor NIST/industry guidance for deprecations or parameter updates.",
            "keywords": ["no monitoring", "no nist", "ignore guidance"],
        },
        {
            "violation": "Has no versioning or metadata to identify which algorithm protected given data.",
            "keywords": ["no versioning", "no metadata", "cannot identify"],
        },
        {
            "violation": "Provides no feature flags or dual-write/dual-read strategy to migrate ciphertexts.",
            "keywords": ["no feature flags", "no dual write", "no strategy"],
        },
    ],
}
