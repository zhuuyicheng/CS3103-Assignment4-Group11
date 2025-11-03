import socket
from typing import Optional, Tuple
from packet import HUDPPacket
from sender import HUDPSender
from receiver import HUDPReceiver


class GameNetAPI:
    """H-UDP API for game networking with reliable and unreliable channels"""
    
    def __init__(self, local_addr: Tuple[str, int], remote_addr: Tuple[str, int]):
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(local_addr)
        
        # Create sender and receiver (they will manage their own threads)
        self.sender = HUDPSender(self.sock, remote_addr)
        self.receiver = HUDPReceiver(self.sock)
        
        # Track packet statistics
        self.sent_reliable = 0
        self.sent_unreliable = 0
    
    def send(self, payload: bytes, reliable: bool = False) -> int:
        """Send data on either reliable or unreliable channel"""
        if reliable:
            seq = self.sender.send_reliable(payload)
            self.sent_reliable += 1
            return seq
        else:
            seq = self.sender.send_unreliable(payload)
            self.sent_unreliable += 1
            return seq

    def recv(self, timeout: Optional[float] = 0.01) -> Optional[HUDPPacket]:
        """Receive data from either channel"""
        return self.receiver.recv(timeout=timeout)

    def close(self):
        """Close the API and cleanup resources"""
        self.sender.close()
        self.receiver.close()
        self.sock.close()
