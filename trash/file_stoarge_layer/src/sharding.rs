// src/sharding.rs

use std::fs::File;
use std::io::{self, Read, Write};

pub const SHARD_SIZE: usize = 4*1024; // 4 KB shards

pub fn shard_file(file_path: &str) -> io::Result<Vec<Vec<u8>>> {
    let mut file = File::open(file_path)?;
    let mut shards = Vec::new();
    let mut buffer = [0; SHARD_SIZE];
    
    while let Ok(read_bytes) = file.read(&mut buffer) {
        if read_bytes == 0 {
            break;
        }
        shards.push(buffer[..read_bytes].to_vec());
    }
    
    Ok(shards)
}

pub fn write_shard(shard: &[u8], shard_number: usize) -> io::Result<()> {
    let mut shard_file = File::create(format!("shard_{}.bin", shard_number))?;
    shard_file.write_all(shard)?;
    Ok(())
}
