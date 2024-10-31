use libp2p::kad::{store::MemoryStore, Kademlia, KademliaEvent, QueryId, QueryResult};
use libp2p::PeerId;

pub fn kad_behavior(local_peer_id: PeerId) -> Kademlia<MemoryStore> {
    Kademlia::new(local_peer_id, MemoryStore::new(local_peer_id))
}

pub fn handle_kad_event(event: KademliaEvent) {
    match event {
        KademliaEvent::OutboundQueryCompleted { result, .. } => match result {
            QueryResult::GetProviders(Ok(providers)) => {
                for peer in providers.providers {
                    println!("Found provider: {:?}", peer);
                }
            }
            QueryResult::Bootstrap(Ok(_)) => println!("Bootstrap completed."),
            _ => {}
        },
        _ => {}
    }
}
