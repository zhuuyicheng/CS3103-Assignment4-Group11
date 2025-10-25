import socket
import threading
import time
from typing import Optional, Tuple
from packet import HUDPPacket, CHANNEL_RELIABLE, CHANNEL_UNRELIABLE, MAX_PACKET_SIZE
from sender import HUDPSender, TIMEOUT
from receiver import HUDPReceiver


class GameNetAPI:
    """H-UDP API for game networking with reliable and unreliable channels"""
    
    def __init__(self, local_addr: Tuple[str, int], remote_addr: Tuple[str, int], 
                 skip_threshold: float = 0.2):
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.skip_threshold = skip_threshold
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(local_addr)
        
        # Create sender and receiver (they will manage their own threads)
        self.sender = HUDPSender(self.sock, remote_addr)
        self.receiver = HUDPReceiver(self.sock)
        
        # Replace receiver's buffer with skip-aware buffer
        self.receiver.reliable_buffer = SkipAwareSelectiveRepeatBuffer(32, skip_threshold)  # type: ignore
        
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
    
    def recv_reliable(self, timeout: Optional[float] = None) -> Optional[HUDPPacket]:
        """Receive from reliable channel (returns full packet for logging)"""
        packet = self.receiver.reliable_buffer.next_packet(timeout)
        return packet
    
    def recv_unreliable(self, timeout: Optional[float] = None) -> Optional[HUDPPacket]:
        """Receive from unreliable channel (returns full packet for logging)"""
        try:
            packet = self.receiver.unreliable_queue.get(timeout=timeout)
            return packet
        except:
            return None
    
    def get_skipped_count(self) -> int:
        """Get the number of packets skipped due to timeout"""
        # The receiver.reliable_buffer may implement different buffer classes;
        # safely return skipped_count if present, otherwise 0.
        return getattr(self.receiver.reliable_buffer, "skipped_count", 0)
    
    def close(self):
        """Close the API and cleanup resources"""
        self.sender.close()
        self.receiver.close()
        try:
            self.sock.close()
        except:
            pass


class SkipAwareSelectiveRepeatBuffer:
    """Selective Repeat buffer with skip logic for missing packets after threshold"""
    
    def __init__(self, window_size: int, skip_threshold: float = 0.2):
        self.window_size = window_size
        self.skip_threshold = skip_threshold
        self.rcv_base = 0
        self.buffer = {}
        self.arrival_times = {}
        self.ready_queue = []
        self.lock = threading.Lock()
        self.skipped_count = 0
    
    def insert(self, packet: HUDPPacket):
        """Insert packet and trigger delivery/skip logic"""
        with self.lock:
            seq = packet.seq_num
            
            # Ignore duplicates or out-of-window packets
            if seq < self.rcv_base:
                return False
            if seq >= self.rcv_base + self.window_size:
                return False
            
            # Store packet
            if seq not in self.buffer:
                self.buffer[seq] = packet
                self.arrival_times[seq] = time.time()
            
            # Try to deliver consecutive packets
            self._deliver_ready_packets()
            
            # Check for skipping logic
            self._check_skip_missing_packets()
            
            return True
    
    def _deliver_ready_packets(self):
        """Deliver all consecutive packets from rcv_base"""
        while self.rcv_base in self.buffer:
            packet = self.buffer.pop(self.rcv_base)
            self.arrival_times.pop(self.rcv_base, None)
            self.ready_queue.append(packet)
            self.rcv_base += 1
    
    def _check_skip_missing_packets(self):
        """Skip missing packets if they exceed the threshold"""
        if self.rcv_base not in self.buffer:
            # Find next available packet
            higher_seqs = [s for s in self.buffer.keys() if s > self.rcv_base]
            if higher_seqs:
                next_seq = min(higher_seqs)
                arrival_time = self.arrival_times.get(next_seq)
                if arrival_time and (time.time() - arrival_time) >= self.skip_threshold:
                    print(f"[Receiver] Skipping missing RELIABLE seq {self.rcv_base} after {self.skip_threshold*1000:.0f} ms")
                    self.skipped_count += 1
                    self.rcv_base += 1
                    # Recursively deliver and check for more skips
                    self._deliver_ready_packets()
                    self._check_skip_missing_packets()
    
    def next_packet(self, timeout: Optional[float] = None) -> Optional[HUDPPacket]:
        """Get next packet from ready queue"""
        start = time.time()
        while True:
            with self.lock:
                # Check skip logic before waiting
                self._check_skip_missing_packets()
                
                if self.ready_queue:
                    return self.ready_queue.pop(0)
            
            # Check timeout
            if timeout is not None and (time.time() - start) >= timeout:
                return None
            
            time.sleep(0.01)
