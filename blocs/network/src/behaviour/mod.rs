use libp2p::PeerId;
use libp2p::{
    gossipsub::{Gossipsub, GossipsubConfig, GossipsubEvent},
    kad::{Kademlia, KademliaConfig, KademliaEvent},
    mdns::{Mdns, MdnsConfig},
    swarm::SwarmEvent,
    NetworkBehaviour,
};

pub mod gossipsub;
pub mod kad;

#[derive(NetworkBehaviour)]
pub struct BlocsBehaviour {
    pub mdns: Mdns,
    pub kademlia: Kademlia,
    pub gossipsub: Gossipsub,
}

impl BlocsBehaviour {
    pub fn new(local_peer_id: PeerId, config: &NetworkConfig) -> Result<Self, String> {
        let mdns = Mdns::new(MdnsConfig::default()).map_err(|e| e.to_string())?;
        let mut kademlia = Kademlia::new(local_peer_id.clone(), KademliaConfig::default());
        let gossipsub = Gossipsub::new(local_peer_id.clone(), GossipsubConfig::default())
            .map_err(|e| e.to_string())?;

        // Add bootstrap peers if any
        for peer_addr in &config.bootstrap_peers {
            let peer_id = peer_addr.parse::<PeerId>().map_err(|e| e.to_string())?;
            kademlia.add_address(&peer_id, peer_addr.clone().parse().unwrap());
        }

        Ok(Self {
            mdns,
            kademlia,
            gossipsub,
        })
    }

    pub fn handle_event(event: SwarmEvent<GossipsubEvent, KademliaEvent>) {
        // Process network events
    }
}
