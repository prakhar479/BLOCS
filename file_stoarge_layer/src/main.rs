// src/main.rs

mod encryption;
mod file_retrieval;
mod metadata;
mod sharding;

use encryption::encrypt_shard;
use file_retrieval::{reassemble_file, retrieve_shard};
use metadata::{load_metadata, save_metadata, ShardMetadata};
use sharding::{shard_file, write_shard};
use std::env;
use std::io;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!(
            "Usage: {} <upload|retrieve> <file_path> <key : Optional>",
            args[0]
        );
        process::exit(1);
    }

    let action = &args[1];
    let file_path = &args[2];
    let key_hex = match args.get(3) {
        Some(key) => key,
        None => {
            println!("Key not provided. Using default key.");
            "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
        }
    };

    if key_hex.len() != 64 {
        println!("Key must be 32 bytes in hex format.");
        process::exit(1);
    }

    match action.as_str() {
        "upload" => {
            if let Err(e) = upload_file(file_path, key_hex) {
                eprintln!("Error uploading file: {}", e);
                process::exit(1);
            }
        }
        "retrieve" => {
            if let Err(e) = retrieve_file(file_path, key_hex) {
                eprintln!("Error retrieving file: {}", e);
                process::exit(1);
            }
        }
        _ => {
            println!("Invalid action. Use 'upload' or 'retrieve'.");
            process::exit(1);
        }
    }
}

fn upload_file(file_path: &str, key_hex: &str) -> io::Result<()> {
    // Convert the hex key string to bytes
    let key: [u8; 32] = hex_to_bytes(key_hex)?
        .try_into()
        .expect("Invalid key length");
    if key.len() != 32 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Key must be 32 bytes.",
        ));
    }

    let shards = shard_file(file_path)?;

    let mut metadata = Vec::new();
    for (i, shard) in shards.iter().enumerate() {
        let encrypted_shard = encrypt_shard(shard, &key).expect("Encryption failed");
        write_shard(&encrypted_shard, i)?;

        let shard_metadata = ShardMetadata {
            shard_id: i,
            file_hash: format!("{:x}", md5::compute(shard)),
            node_address: "node_address".to_string(), // Placeholder for actual node address
        };
        metadata.push(shard_metadata);
    }
    save_metadata(&metadata, "metadata.json")?;
    Ok(())
}

fn retrieve_file(file_path: &str, key_hex: &str) -> io::Result<()> {
    // Convert the hex key string to bytes
    let key: [u8; 32] = hex_to_bytes(key_hex)?
        .try_into()
        .expect("Invalid key length");
    if key.len() != 32 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Key must be 32 bytes.",
        ));
    }

    let metadata = load_metadata("metadata.json")?;

    let mut shards = Vec::new();
    for data in metadata.iter() {
        let shard = retrieve_shard(&format!("shard_{}.bin", data.shard_id), &key)
            .expect("Error retrieving shard");
        shards.push(shard);
    }

    reassemble_file(shards, file_path)?;
    Ok(())
}

/// Converts a hex string to a byte vector.
fn hex_to_bytes(hex: &str) -> io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    let hex_len = hex.len();

    if hex_len % 2 != 0 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Hex string must have an even length.",
        ));
    }

    for i in (0..hex_len).step_by(2) {
        let byte_str = &hex[i..i + 2];
        let byte = u8::from_str_radix(byte_str, 16)
            .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "Invalid hex digit."))?;
        bytes.push(byte);
    }

    Ok(bytes)
}
