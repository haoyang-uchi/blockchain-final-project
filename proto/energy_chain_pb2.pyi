from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PUSH: _ClassVar[OrderType]
    PULL: _ClassVar[OrderType]
PUSH: OrderType
PULL: OrderType

class SubmitResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetTipRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBlocksRequest(_message.Message):
    __slots__ = ("start_height", "end_height")
    START_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    END_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    start_height: int
    end_height: int
    def __init__(self, start_height: _Optional[int] = ..., end_height: _Optional[int] = ...) -> None: ...

class GetBlocksResponse(_message.Message):
    __slots__ = ("blocks",)
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    blocks: _containers.RepeatedCompositeFieldContainer[Block]
    def __init__(self, blocks: _Optional[_Iterable[_Union[Block, _Mapping]]] = ...) -> None: ...

class GetPeersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPeersResponse(_message.Message):
    __slots__ = ("peer_addresses",)
    PEER_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    peer_addresses: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, peer_addresses: _Optional[_Iterable[str]] = ...) -> None: ...

class RegistrationRequest(_message.Message):
    __slots__ = ("nVersion", "nTime", "addrMe")
    NVERSION_FIELD_NUMBER: _ClassVar[int]
    NTIME_FIELD_NUMBER: _ClassVar[int]
    ADDRME_FIELD_NUMBER: _ClassVar[int]
    nVersion: int
    nTime: float
    addrMe: str
    def __init__(self, nVersion: _Optional[int] = ..., nTime: _Optional[float] = ..., addrMe: _Optional[str] = ...) -> None: ...

class RegistrationReply(_message.Message):
    __slots__ = ("success", "last_registered")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    LAST_REGISTERED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    last_registered: str
    def __init__(self, success: bool = ..., last_registered: _Optional[str] = ...) -> None: ...

class Block(_message.Message):
    __slots__ = ("header", "transactions")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    header: Header
    transactions: _containers.RepeatedCompositeFieldContainer[Transaction]
    def __init__(self, header: _Optional[_Union[Header, _Mapping]] = ..., transactions: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ...) -> None: ...

class Header(_message.Message):
    __slots__ = ("version", "hash_prev_block", "hash_merkle_root", "timestamp", "bits", "nonce", "height")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    HASH_PREV_BLOCK_FIELD_NUMBER: _ClassVar[int]
    HASH_MERKLE_ROOT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BITS_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    version: int
    hash_prev_block: str
    hash_merkle_root: str
    timestamp: int
    bits: int
    nonce: int
    height: int
    def __init__(self, version: _Optional[int] = ..., hash_prev_block: _Optional[str] = ..., hash_merkle_root: _Optional[str] = ..., timestamp: _Optional[int] = ..., bits: _Optional[int] = ..., nonce: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("transaction_hash", "grid_rate_tx", "order_tx", "trade_tx")
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    GRID_RATE_TX_FIELD_NUMBER: _ClassVar[int]
    ORDER_TX_FIELD_NUMBER: _ClassVar[int]
    TRADE_TX_FIELD_NUMBER: _ClassVar[int]
    transaction_hash: str
    grid_rate_tx: GridRateTx
    order_tx: OrderTx
    trade_tx: TradeTx
    def __init__(self, transaction_hash: _Optional[str] = ..., grid_rate_tx: _Optional[_Union[GridRateTx, _Mapping]] = ..., order_tx: _Optional[_Union[OrderTx, _Mapping]] = ..., trade_tx: _Optional[_Union[TradeTx, _Mapping]] = ...) -> None: ...

class GridRateTx(_message.Message):
    __slots__ = ("push_rate", "pull_rate", "expiry_height", "grid_address", "signature")
    PUSH_RATE_FIELD_NUMBER: _ClassVar[int]
    PULL_RATE_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    GRID_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    push_rate: int
    pull_rate: int
    expiry_height: int
    grid_address: str
    signature: bytes
    def __init__(self, push_rate: _Optional[int] = ..., pull_rate: _Optional[int] = ..., expiry_height: _Optional[int] = ..., grid_address: _Optional[str] = ..., signature: _Optional[bytes] = ...) -> None: ...

class OrderTx(_message.Message):
    __slots__ = ("sender_address", "type", "energy_wh", "limit_price", "nonce", "script", "signature")
    SENDER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ENERGY_WH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    sender_address: str
    type: OrderType
    energy_wh: int
    limit_price: int
    nonce: int
    script: str
    signature: bytes
    def __init__(self, sender_address: _Optional[str] = ..., type: _Optional[_Union[OrderType, str]] = ..., energy_wh: _Optional[int] = ..., limit_price: _Optional[int] = ..., nonce: _Optional[int] = ..., script: _Optional[str] = ..., signature: _Optional[bytes] = ...) -> None: ...

class TradeTx(_message.Message):
    __slots__ = ("miner_address", "order", "grid_rate", "miner_fee", "settlement_amount")
    MINER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    GRID_RATE_FIELD_NUMBER: _ClassVar[int]
    MINER_FEE_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    miner_address: str
    order: OrderTx
    grid_rate: GridRateTx
    miner_fee: int
    settlement_amount: int
    def __init__(self, miner_address: _Optional[str] = ..., order: _Optional[_Union[OrderTx, _Mapping]] = ..., grid_rate: _Optional[_Union[GridRateTx, _Mapping]] = ..., miner_fee: _Optional[int] = ..., settlement_amount: _Optional[int] = ...) -> None: ...
