pub mod config;
pub mod error;
pub mod behaviour;
pub mod protocol;
pub mod discovery;

use libp2p::{Multiaddr, PeerId, Swarm};
use behaviour::BlocsBehaviour;
use config::NetworkConfig;
use discovery::DHT;
use error::NetworkError;
use futures::executor::block_on;

pub struct Network {
    pub swarm: Swarm<BlocsBehaviour>,
}

impl Network {
    pub fn new(config: NetworkConfig) -> Result<Self, NetworkError> {
        let local_key = config.generate_local_key()?;
        let local_peer_id = PeerId::from(local_key.public());
        let behaviour = BlocsBehaviour::new(local_peer_id, &config)?;

        Ok(Network {
            swarm: Swarm::new(config.build_transport(local_key)?, behaviour, local_peer_id),
        })
    }

    pub fn start(&mut self, listen_addr: Multiaddr) -> Result<(), NetworkError> {
        Swarm::listen_on(&mut self.swarm, listen_addr)?;
        println!("Listening on {:?}", listen_addr);

        block_on(async {
            while let Some(event) = self.swarm.next().await {
                // Handle each event
            }
        });

        Ok(())
    }
}
