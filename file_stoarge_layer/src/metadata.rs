// src/metadata.rs

use serde::{Deserialize, Serialize};
// use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read, Write};

#[derive(Serialize, Deserialize, Debug)]
pub struct ShardMetadata {
    pub shard_id: usize,
    pub file_hash: String,
    pub node_address: String,
}

pub fn save_metadata(metadata: &Vec<ShardMetadata>, file_name: &str) -> io::Result<()> {
    let serialized = serde_json::to_string(&metadata)?;
    let mut file = File::create(file_name)?;
    file.write_all(serialized.as_bytes())?;
    Ok(())
}

pub fn load_metadata(file_name: &str) -> io::Result<Vec<ShardMetadata>> {
    let mut file = File::open(file_name)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let metadata: Vec<ShardMetadata> = serde_json::from_str(&contents)?;
    Ok(metadata)
}
