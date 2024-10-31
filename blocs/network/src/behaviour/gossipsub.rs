use libp2p::gossipsub::{Gossipsub, GossipsubConfig, MessageId, Topic};
use libp2p::PeerId;

pub fn gossip_behavior(local_peer_id: PeerId) -> Gossipsub {
    Gossipsub::new(local_peer_id, GossipsubConfig::default()).expect("Failed to create Gossipsub")
}

pub fn handle_gossip_event(message_id: MessageId, message: Vec<u8>, sender: PeerId) {
    println!(
        "Received message from {:?}: {:?}",
        sender,
        String::from_utf8_lossy(&message)
    );
}
