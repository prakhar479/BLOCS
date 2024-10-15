// src/encryption.rs

use aes_gcm::aead::{Aead, KeyInit, OsRng, generic_array::GenericArray};
use aes_gcm::{Aes256Gcm, Nonce};
use aes_gcm::aead::rand_core::RngCore;
use aes_gcm::aead::Error as AeadError;

pub fn encrypt_shard(shard: &[u8], key: &[u8; 32]) -> Result<Vec<u8>, AeadError> {
    let cipher = Aes256Gcm::new(GenericArray::from_slice(key));

    let mut nonce = [0u8; 12];
    OsRng.fill_bytes(&mut nonce);
    let nonce = Nonce::from_slice(&nonce);

    let encrypted_data = cipher.encrypt(nonce, shard)?;

    Ok([nonce.as_slice(), &encrypted_data].concat())
}

pub fn decrypt_shard(encrypted_shard: &[u8], key: &[u8; 32]) -> Result<Vec<u8>, AeadError> {
    let cipher = Aes256Gcm::new(GenericArray::from_slice(key));

    let (nonce, ciphertext) = encrypted_shard.split_at(12);
    let nonce = Nonce::from_slice(nonce);

    cipher.decrypt(nonce, ciphertext)
}

#[cfg(test)]
mod tests {
    use super::*;
    use aes_gcm::aead::rand_core::OsRng;

    #[test]
    fn test_encrypt_decrypt() {
        let shard_data = b"Test data for encryption";
        
        let mut key = [0u8; 32];
        OsRng.fill_bytes(&mut key);

        let encrypted_shard = encrypt_shard(shard_data, &key).expect("Encryption failed");
        let decrypted_shard = decrypt_shard(&encrypted_shard, &key).expect("Decryption failed");

        assert_eq!(shard_data.to_vec(), decrypted_shard);
    }

    #[test]
    fn test_empty_input() {
        let shard_data: &[u8] = b"";
        
        let mut key = [0u8; 32];
        OsRng.fill_bytes(&mut key);

        let encrypted_shard = encrypt_shard(shard_data, &key).expect("Encryption failed");
        let decrypted_shard = decrypt_shard(&encrypted_shard, &key).expect("Decryption failed");

        assert_eq!(shard_data.to_vec(), decrypted_shard);
    }

    #[test]
    fn test_decryption_with_wrong_key() {
        let shard_data = b"Test data with wrong key";
        
        let mut key = [0u8; 32];
        OsRng.fill_bytes(&mut key);

        let encrypted_shard = encrypt_shard(shard_data, &key).expect("Encryption failed");

        let mut wrong_key = [0u8; 32];
        OsRng.fill_bytes(&mut wrong_key);

        let result = decrypt_shard(&encrypted_shard, &wrong_key);
        assert!(result.is_err(), "Decryption should fail with the wrong key");
    }
}
