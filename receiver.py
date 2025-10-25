import socket
import time
import threading
from typing import Dict, Tuple, Optional
import queue
from packet import HUDPPacket, CHANNEL_RELIABLE, CHANNEL_UNRELIABLE, MAX_PACKET_SIZE
from sender import WINDOW_SIZE

class HUDPReceiver:
    """H-UDP receiver with demultiplexing and selective repeat"""
    
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.reliable_buffer = SelectiveRepeatBuffer(WINDOW_SIZE)
        self.unreliable_queue = queue.Queue()
        self.shutdown_event = threading.Event()
        
        # Start receiver thread
        self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receiver_thread.start()
    
    def _receive_loop(self):
        """Background thread to receive and demultiplex packets"""
        while not self.shutdown_event.is_set():
            try:
                self.sock.settimeout(0.1)
                data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
                packet = HUDPPacket.deserialize(data)
                
                if packet.channel_type == CHANNEL_RELIABLE:
                    self._handle_reliable(packet, addr)
                elif packet.channel_type == CHANNEL_UNRELIABLE:
                    self._handle_unreliable(packet)
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receiver error: {e}")
    
    def _handle_reliable(self, packet: HUDPPacket, addr: Tuple[str, int]):
        """Handle reliable channel packet with selective repeat"""
        # Insert into buffer
        self.reliable_buffer.insert(packet)
        
        # By right only need to ACK packets with seq_num in [rcv_base - WINDOW_SIZE, rcv_base - 1]
        # but to keep it simple, we ACK every received packet
        ack_packet = HUDPPacket(
            channel_type=CHANNEL_RELIABLE,
            seq_num=0,
            ack_num=packet.seq_num,
            timestamp=time.time(),
            payload=b''
        )
        self.sock.sendto(ack_packet.serialize(), addr)
    
    def _handle_unreliable(self, packet: HUDPPacket):
        """Handle unreliable channel packet (no ACK)"""
        self.unreliable_queue.put(packet)
    
    def recv_reliable(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """Receive data from reliable channel (ordered)"""
        packet = self.reliable_buffer.next_packet(timeout)
        return packet.payload if packet else None
    
    def recv_unreliable(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """Receive data from unreliable channel (unordered)"""
        try:
            packet = self.unreliable_queue.get(timeout=timeout)
            return packet.payload
        except queue.Empty:
            return None
    
    def close(self):
        """Stop receiver thread"""
        self.shutdown_event.set()
        if self.receiver_thread.is_alive():
            self.receiver_thread.join()


class SelectiveRepeatBuffer:
    """Buffer for reordering reliable packets using Selective Repeat"""
    
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.rcv_base = 0  # Next expected sequence number
        self.buffer: Dict[int, HUDPPacket] = {}
        self.ready_queue = queue.Queue()
    
    def insert(self, packet: HUDPPacket) -> bool:
        """Insert packet into buffer and check if it's in window"""
        seq = packet.seq_num
        
        # Check if packet is within window
        if seq < self.rcv_base:
            # Duplicate packet, already delivered
            return False
        
        if seq >= self.rcv_base + self.window_size:
            # Out of window, drop
            return False
        
        # Add to buffer if not already received
        if seq not in self.buffer:
            self.buffer[seq] = packet
        
        # Deliver consecutive packets starting from rcv_base
        self._deliver_ready_packets()
        return True
    
    def _deliver_ready_packets(self):
        """Deliver all consecutive packets from rcv_base"""
        while self.rcv_base in self.buffer:
            packet = self.buffer.pop(self.rcv_base)
            self.ready_queue.put(packet)
            self.rcv_base += 1
    
    def next_packet(self, timeout: Optional[float] = None) -> Optional[HUDPPacket]:
        """Get next ordered packet (blocking)"""
        try:
            return self.ready_queue.get(timeout=timeout)
        except queue.Empty:
            return None
        