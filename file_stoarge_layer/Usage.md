
# Usage Guide for the File Encryption Tool

## Overview

This tool allows users to upload files securely by encrypting them into shards and later retrieving the original file from these shards. It utilizes AES encryption for secure file storage.

## Requirements

- Rust programming language installed on your system.
- `Cargo` (comes with Rust) for building and managing dependencies.

## Getting Started

1. **Clone the Repository**:
   If you haven't done so already, clone the repository containing the code.

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Build the Project**:
   Build the project using Cargo:

   ```bash
   cargo build --release
   ```

3. **Run the Application**:
   The application can be run from the command line using the following syntax:

   ```bash
   ./target/release/file_encryption_tool <upload|retrieve> <file_path> <key>
   ```

## Commands

### 1. Upload Command

**Syntax**:

```bash
./target/release/file_encryption_tool upload <file_path> <key>
```

**Parameters**:
- `<file_path>`: The path to the file you want to upload (e.g., `data.txt`).
- `<key>`: A 32-byte hexadecimal string representing the AES encryption key (e.g., `00112233445566778899aabbccddeeff`).

**Description**:
This command splits the specified file into shards, encrypts each shard using the provided key, and saves the metadata and shards to the local file system.

**Example**:

```bash
./target/release/file_encryption_tool upload data.txt 00112233445566778899aabbccddeeff
```

### 2. Retrieve Command

**Syntax**:

```bash
./target/release/file_encryption_tool retrieve <output_file_path> <key>
```

**Parameters**:
- `<output_file_path>`: The path where the retrieved file will be saved (e.g., `output.txt`).
- `<key>`: A 32-byte hexadecimal string representing the AES encryption key (e.g., `00112233445566778899aabbccddeeff`).

**Description**:
This command retrieves the encrypted shards, decrypts them using the provided key, and reassembles them into the original file.

**Example**:

```bash
./target/release/file_encryption_tool retrieve output.txt 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff
```

## Key Format

The key must be a 32-byte hexadecimal string. Here are some valid examples:

- `00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff`
- `abcdefabcdefabcdefabcdefabcdefab00112233445566778899aabbccddeeff`

### Invalid Key Format

If the key is not 32 bytes long or is not a valid hexadecimal string, the program will terminate with an error message.

## Error Handling

The program provides error messages for the following scenarios:

- Incorrect command usage (e.g., missing required parameters).
- Invalid action (should be either `upload` or `retrieve`).
- Key does not conform to the expected format.
- File read/write errors (e.g., if the file does not exist or cannot be accessed).
