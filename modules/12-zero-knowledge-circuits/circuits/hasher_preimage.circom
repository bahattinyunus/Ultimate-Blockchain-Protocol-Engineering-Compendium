pragma circom 2.1.6;

/**
 * @title HasherPreimageProof
 * @notice Demonstrates Zero-Knowledge proof of knowledge of a secret preimage
 * without revealing the preimage to the verifier.
 *
 * Public Input: expectedHash
 * Private Inputs: secretPreimage, secretSalt
 */

template HasherPreimageProof() {
    // === 1. DECLARE SIGNALS ===
    // Public signals
    signal input expectedHash;

    // Private witness signals
    signal input secretPreimage;
    signal input secretSalt;

    // Intermediate computation signals
    signal intermediateSquare;
    signal computedHash;

    // === 2. ARITHMETIC CONSTRAINTS (R1CS) ===
    // Constraint 1: intermediateSquare = secretPreimage * secretPreimage
    intermediateSquare <== secretPreimage * secretPreimage;

    // Constraint 2: computedHash = intermediateSquare * secretSalt + 42
    // Formulated as Rank-1 quadratic gate:
    signal saltProduct;
    saltProduct <== intermediateSquare * secretSalt;
    computedHash <== saltProduct + 42;

    // === 3. ASSERTION ===
    // Constraint 3: Verify computed hash matches public expectedHash
    computedHash === expectedHash;
}

component main {public [expectedHash]} = HasherPreimageProof();
