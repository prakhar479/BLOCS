// src/file_retrieval.rs

use crate::encryption::decrypt_shard;
use std::error::Error;
use std::fs::{read, File};
use std::io::{self, Write};

pub fn retrieve_shard(file_path: &str, key: &[u8; 32]) -> Result<Vec<u8>, Box<dyn Error>> {
    let encrypted_shard = read(file_path)?;

    let decrypted_shard = decrypt_shard(&encrypted_shard, key).map_err(|e| Box::<dyn Error>::from(e.to_string()))?;

    Ok(decrypted_shard)
}

pub fn reassemble_file(shards: Vec<Vec<u8>>, output_path: &str) -> io::Result<()> {
    let mut file = File::create(output_path)?;
    for shard in shards {
        file.write_all(&shard)?;
    }
    Ok(())
}
