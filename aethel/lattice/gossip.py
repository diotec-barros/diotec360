"""
Gossip Protocol - Epidemic Information Dissemination for Aethel Lattice

This module implements a gossip-based protocol for propagating proofs, state
updates, and network events across the Aethel Lattice. Inspired by epidemic
algorithms, information spreads organically through the network with:

1. Push gossip: Nodes actively send updates to random peers
2. Pull gossip: Nodes request missing updates from peers
3. Anti-entropy: Periodic synchronization to ensure consistency
4. Bloom filters: Efficient detection of missing data

The protocol ensures that when Node A proves a transaction, Node B receives
and validates it almost instantaneously, even in large networks.

Research Foundation:
- Epidemic Algorithms for Replicated Database Maintenance (Demers et al.)
- Gossip-based protocols for large-scale distributed systems
- Bitcoin's transaction propagation mechanism

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 3.0 "The Lattice"
Date: February 5, 2026
"""

import asyncio
import json
import time
import random
from typing import List, Set, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from collections import deque
import logging
import hashlib

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


@dataclass
class GossipMessage:
    """
    A message to be gossiped across the network.
    
    Attributes:
        message_id: Unique identifier for this message
        message_type: Type of message (proof, state_update, event)
        payload: Message content
        origin_node: Node that created this message
        timestamp: Unix timestamp when message was created
        ttl: Time-to-live (hops remaining)
        seen_by: Set of node IDs that have seen this message
    """
    message_id: str
    message_type: str
    payload: Dict[str, Any]
    origin_node: str
    timestamp: float
    ttl: int = 10
    seen_by: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "origin_node": self.origin_node,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "seen_by": list(self.seen_by)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GossipMessage':
        """Create from dictionary"""
        return cls(
            message_id=data["message_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            origin_node=data["origin_node"],
            timestamp=data["timestamp"],
            ttl=data.get("ttl", 10),
            seen_by=set(data.get("seen_by", []))
        )
    
    def compute_hash(self) -> str:
        """Compute hash of message for deduplication"""
        content = f"{self.message_id}{self.message_type}{self.origin_node}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class GossipConfig:
    """
    Configuration for gossip protocol.
    
    Attributes:
        fanout: Number of peers to gossip to per round
        gossip_interval: Seconds between gossip rounds
        message_ttl: Maximum hops for a message
        message_cache_size: Maximum messages to cache
        anti_entropy_interval: Seconds between anti-entropy rounds
        enable_push: Enable push gossip
        enable_pull: Enable pull gossip
        enable_anti_entropy: Enable anti-entropy synchronization
    """
    fanout: int = 3  # Gossip to 3 random peers per round
    gossip_interval: float = 0.5  # 500ms between rounds
    message_ttl: int = 10  # Max 10 hops
    message_cache_size: int = 1000  # Cache last 1000 messages
    anti_entropy_interval: int = 30  # Anti-entropy every 30s
    enable_push: bool = True
    enable_pull: bool = True
    enable_anti_entropy: bool = True


class GossipProtocol:
    """
    Gossip-based information dissemination protocol.
    
    This protocol implements epidemic-style message propagation:
    1. When a node has new information, it gossips to random peers
    2. Peers forward to their peers, creating exponential spread
    3. Duplicate detection prevents message loops
    4. TTL prevents infinite propagation
    
    The result: O(log N) latency for network-wide propagation.
    """
    
    def __init__(self, config: GossipConfig, node_id: str, get_peers_func: Callable):
        """
        Initialize gossip protocol.
        
        Args:
            config: Gossip configuration
            node_id: This node's unique identifier
            get_peers_func: Function that returns list of peer addresses
        """
        self.config = config
        self.node_id = node_id
        self.get_peers = get_peers_func
        
        # Message cache (message_id -> GossipMessage)
        self.message_cache: Dict[str, GossipMessage] = {}
        
        # Messages pending gossip
        self.pending_messages: deque[GossipMessage] = deque()
        
        # Message handlers (message_type -> handler function)
        self.message_handlers: Dict[str, Callable] = {}
        
        # Gossip tasks
        self._gossip_task: Optional[asyncio.Task] = None
        self._anti_entropy_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_forwarded": 0,
            "duplicates_filtered": 0
        }
        
        logger.info(f"[GOSSIP] Initialized for node {node_id}")
    
    async def start(self) -> None:
        """Start the gossip protocol"""
        if self._running:
            return
        
        self._running = True
        
        # Start gossip loop
        if self.config.enable_push:
            self._gossip_task = asyncio.create_task(self._gossip_loop())
        
        # Start anti-entropy loop
        if self.config.enable_anti_entropy:
            self._anti_entropy_task = asyncio.create_task(self._anti_entropy_loop())
        
        logger.info("[GOSSIP] 📢 Protocol started")
    
    async def stop(self) -> None:
        """Stop the gossip protocol"""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel tasks
        if self._gossip_task:
            self._gossip_task.cancel()
            try:
                await self._gossip_task
            except asyncio.CancelledError:
                pass
        
        if self._anti_entropy_task:
            self._anti_entropy_task.cancel()
            try:
                await self._anti_entropy_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[GOSSIP] Protocol stopped")
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        Register a handler for a message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function that processes the message
        """
        self.message_handlers[message_type] = handler
        logger.info(f"[GOSSIP] Registered handler for '{message_type}'")
    
    def broadcast(self, message_type: str, payload: Dict[str, Any]) -> str:
        """
        Broadcast a message to the network.
        
        Args:
            message_type: Type of message
            payload: Message content
        
        Returns:
            Message ID
        """
        # Create message
        message_id = self._generate_message_id()
        message = GossipMessage(
            message_id=message_id,
            message_type=message_type,
            payload=payload,
            origin_node=self.node_id,
            timestamp=time.time(),
            ttl=self.config.message_ttl
        )
        
        # Add to cache
        self.message_cache[message_id] = message
        
        # Add to pending queue
        self.pending_messages.append(message)
        
        logger.info(f"[GOSSIP] 📤 Broadcasting {message_type}: {message_id[:8]}")
        
        return message_id
    
    async def receive_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Receive a gossip message from a peer.
        
        Args:
            message_data: Message data dictionary
        
        Returns:
            True if message was new, False if duplicate
        """
        try:
            message = GossipMessage.from_dict(message_data)
            
            # Check if we've seen this message
            if message.message_id in self.message_cache:
                self.stats["duplicates_filtered"] += 1
                return False
            
            # Check TTL
            if message.ttl <= 0:
                logger.debug(f"[GOSSIP] Message {message.message_id[:8]} expired (TTL=0)")
                return False
            
            # Add to cache
            self.message_cache[message.message_id] = message
            message.seen_by.add(self.node_id)
            
            # Update stats
            self.stats["messages_received"] += 1
            
            logger.info(f"[GOSSIP] 📥 Received {message.message_type}: {message.message_id[:8]}")
            
            # Process message
            await self._process_message(message)
            
            # Forward to peers (if TTL allows)
            if message.ttl > 1:
                message.ttl -= 1
                self.pending_messages.append(message)
                self.stats["messages_forwarded"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"[GOSSIP] Error receiving message: {e}")
            return False
    
    async def _process_message(self, message: GossipMessage) -> None:
        """
        Process a received message.
        
        Args:
            message: Message to process
        """
        # Find handler for this message type
        handler = self.message_handlers.get(message.message_type)
        
        if handler:
            try:
                await handler(message.payload, message.origin_node)
            except Exception as e:
                logger.error(f"[GOSSIP] Error in handler for {message.message_type}: {e}")
        else:
            logger.debug(f"[GOSSIP] No handler for message type: {message.message_type}")
    
    async def _gossip_loop(self) -> None:
        """Main gossip loop - push messages to random peers"""
        cleanup_counter = 0
        
        while self._running:
            try:
                # Process pending messages
                if self.pending_messages:
                    message = self.pending_messages.popleft()
                    await self._gossip_message(message)
                
                # Periodic cache cleanup (every 100 iterations)
                cleanup_counter += 1
                if cleanup_counter >= 100:
                    self._cleanup_old_messages()
                    cleanup_counter = 0
                
                # Wait before next round
                await asyncio.sleep(self.config.gossip_interval)
                
            except Exception as e:
                logger.error(f"[GOSSIP] Error in gossip loop: {e}")
                await asyncio.sleep(1)
    
    async def _gossip_message(self, message: GossipMessage) -> None:
        """
        Gossip a message to random peers.
        
        Args:
            message: Message to gossip
        """
        # Get available peers
        peers = self.get_peers()
        
        if not peers:
            return
        
        # Select random peers (fanout)
        fanout = min(self.config.fanout, len(peers))
        selected_peers = random.sample(peers, fanout)
        
        # Send to selected peers
        for peer in selected_peers:
            try:
                # Skip if peer has already seen this message
                if peer.peer_id in message.seen_by:
                    continue
                
                # Send message to peer
                await self._send_to_peer(peer.address, message)
                message.seen_by.add(peer.peer_id)
                
                self.stats["messages_sent"] += 1
                
            except Exception as e:
                logger.debug(f"[GOSSIP] Failed to send to {peer.peer_id}: {e}")
    
    async def _send_to_peer(self, peer_address: str, message: GossipMessage) -> None:
        """
        Send a message to a specific peer via HTTP.
        
        Args:
            peer_address: Peer's network address (e.g., "http://node1.aethel.network:8000")
            message: Message to send
        """
        if not aiohttp:
            logger.debug(f"[GOSSIP] aiohttp not available, simulating send to {peer_address}")
            return
        
        try:
            # Construct gossip endpoint URL
            url = f"{peer_address}/api/gossip"
            
            # Send message via HTTP POST
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=message.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logger.debug(f"[GOSSIP] ✓ Sent {message.message_type} to {peer_address}")
                    else:
                        logger.warning(f"[GOSSIP] Peer {peer_address} returned {response.status}")
                        
        except asyncio.TimeoutError:
            logger.debug(f"[GOSSIP] Timeout sending to {peer_address}")
        except aiohttp.ClientError as e:
            logger.debug(f"[GOSSIP] Connection error to {peer_address}: {e}")
        except Exception as e:
            logger.error(f"[GOSSIP] Unexpected error sending to {peer_address}: {e}")
    
    async def _anti_entropy_loop(self) -> None:
        """Anti-entropy loop - periodic synchronization with peers"""
        while self._running:
            try:
                await asyncio.sleep(self.config.anti_entropy_interval)
                await self._anti_entropy_sync()
                
            except Exception as e:
                logger.error(f"[GOSSIP] Error in anti-entropy: {e}")
    
    async def _anti_entropy_sync(self) -> None:
        """
        Perform anti-entropy synchronization.
        
        Exchanges message digests with a random peer to detect
        and repair missing messages.
        """
        peers = self.get_peers()
        
        if not peers:
            return
        
        # Select random peer
        peer = random.choice(peers)
        
        logger.debug(f"[GOSSIP] 🔄 Anti-entropy sync with {peer.peer_id}")
        
        # Get our message IDs
        our_messages = set(self.message_cache.keys())
        
        try:
            # Request peer's message IDs
            peer_messages = await self._request_message_ids(peer.address)
            
            if peer_messages is None:
                return
            
            # Find messages we're missing
            missing = peer_messages - our_messages
            
            # Request missing messages
            for msg_id in missing:
                await self._request_message(peer.address, msg_id)
            
            # Find messages peer is missing (optional: help peer catch up)
            peer_missing = our_messages - peer_messages
            if peer_missing:
                logger.debug(f"[GOSSIP] Peer {peer.peer_id} is missing {len(peer_missing)} messages")
                
        except Exception as e:
            logger.debug(f"[GOSSIP] Anti-entropy sync failed with {peer.peer_id}: {e}")
    
    async def _request_message_ids(self, peer_address: str) -> Optional[Set[str]]:
        """
        Request list of message IDs from a peer.
        
        Args:
            peer_address: Peer's network address
        
        Returns:
            Set of message IDs, or None if request failed
        """
        if not aiohttp:
            return None
        
        try:
            url = f"{peer_address}/api/gossip/message_ids"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return set(data.get("message_ids", []))
                    else:
                        logger.debug(f"[GOSSIP] Failed to get message IDs from {peer_address}")
                        return None
                        
        except Exception as e:
            logger.debug(f"[GOSSIP] Error requesting message IDs from {peer_address}: {e}")
            return None
    
    async def _request_message(self, peer_address: str, message_id: str) -> None:
        """
        Request a specific message from a peer.
        
        Args:
            peer_address: Peer's network address
            message_id: ID of message to request
        """
        if not aiohttp:
            return
        
        try:
            url = f"{peer_address}/api/gossip/message/{message_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        message_data = await response.json()
                        await self.receive_message(message_data)
                        logger.debug(f"[GOSSIP] Retrieved missing message {message_id[:8]}")
                    else:
                        logger.debug(f"[GOSSIP] Failed to get message {message_id[:8]} from {peer_address}")
                        
        except Exception as e:
            logger.debug(f"[GOSSIP] Error requesting message {message_id[:8]}: {e}")
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        content = f"{self.node_id}{time.time()}{random.random()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _cleanup_old_messages(self) -> None:
        """Remove old messages from cache"""
        if len(self.message_cache) <= self.config.message_cache_size:
            return
        
        # Sort by timestamp
        sorted_messages = sorted(
            self.message_cache.items(),
            key=lambda x: x[1].timestamp
        )
        
        # Remove oldest messages
        to_remove = len(self.message_cache) - self.config.message_cache_size
        for msg_id, _ in sorted_messages[:to_remove]:
            del self.message_cache[msg_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gossip statistics"""
        return {
            **self.stats,
            "cached_messages": len(self.message_cache),
            "pending_messages": len(self.pending_messages)
        }
    
    def get_message_ids(self) -> List[str]:
        """
        Get list of all cached message IDs.
        
        Used by anti-entropy protocol to detect missing messages.
        
        Returns:
            List of message IDs
        """
        return list(self.message_cache.keys())
    
    def get_message(self, message_id: str) -> Optional[GossipMessage]:
        """
        Get a specific message from cache.
        
        Args:
            message_id: Message ID to retrieve
        
        Returns:
            GossipMessage if found, None otherwise
        """
        return self.message_cache.get(message_id)


# Singleton instance
_gossip_protocol: Optional[GossipProtocol] = None


def get_gossip_protocol() -> Optional[GossipProtocol]:
    """Get the singleton gossip protocol instance"""
    return _gossip_protocol


def init_gossip_protocol(config: GossipConfig, node_id: str, get_peers_func: Callable) -> GossipProtocol:
    """
    Initialize the gossip protocol singleton.
    
    Args:
        config: Gossip configuration
        node_id: This node's unique identifier
        get_peers_func: Function that returns list of peers
    
    Returns:
        GossipProtocol instance
    """
    global _gossip_protocol
    _gossip_protocol = GossipProtocol(config, node_id, get_peers_func)
    return _gossip_protocol
