#[derive(Debug)]
pub enum NetworkError {
    TransportError(String),
    SwarmError(String),
}

impl
    From<
        libp2p::TransportError<
            libp2p::core::either::EitherError<
                libp2p::core::identity::error::Error,
                libp2p::core::upgrade::UpgradeError,
            >,
        >,
    > for NetworkError
{
    fn from(
        error: libp2p::TransportError<
            libp2p::core::either::EitherError<
                libp2p::core::identity::error::Error,
                libp2p::core::upgrade::UpgradeError,
            >,
        >,
    ) -> Self {
        NetworkError::TransportError(format!("{:?}", error))
    }
}
