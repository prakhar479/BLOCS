use libp2p::identity::Keypair;
use libp2p::{identity, noise, tcp, yamux, Transport};

pub struct NetworkConfig {
    pub key_seed: Option<u8>,         // Seed for generating local key, if needed
    pub bootstrap_peers: Vec<String>, // List of bootstrap peers
}

impl NetworkConfig {
    pub fn generate_local_key(&self) -> Result<Keypair, String> {
        if let Some(seed) = self.key_seed {
            Ok(Keypair::generate_ed25519_from(seed))
        } else {
            Ok(Keypair::generate_ed25519())
        }
    }

    pub fn build_transport(&self, local_key: Keypair) -> Result<impl Transport, String> {
        Ok(tcp::TcpConfig::new()
            .upgrade(yamux::Config::default())
            .authenticate(noise::NoiseConfig::xx(local_key)?)
            .multiplex(yamux::Config::default())
            .boxed())
    }
}
