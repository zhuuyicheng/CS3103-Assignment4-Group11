import socket
import time
import threading
from typing import Dict, Tuple, Optional
import queue
from packet import HUDPPacket, CHANNEL_RELIABLE, CHANNEL_UNRELIABLE, MAX_PACKET_SIZE
from sender import WINDOW_SIZE, MAX_SEND_RATE

class HUDPReceiver:
    """H-UDP receiver with demultiplexing and selective repeat"""
    
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.ready_queue = queue.Queue() # thread-safe
        self.reliable_buffer = SelectiveRepeatBuffer(WINDOW_SIZE, self.ready_queue)
        self.shutdown_event = threading.Event()
        
        # Start receiver thread
        self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receiver_thread.start()
    
    def _receive_loop(self):
        """Background thread to receive and demultiplex packets"""
        while not self.shutdown_event.is_set():
            try:
                self.sock.settimeout(1 / MAX_SEND_RATE)
                data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
                packet = HUDPPacket.deserialize(data)
                
                if packet.channel_type == CHANNEL_RELIABLE:
                    self._handle_reliable(packet, addr)
                elif packet.channel_type == CHANNEL_UNRELIABLE:
                    self._handle_unreliable(packet)
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Receiver] Error: {e}")
    
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
        self.ready_queue.put(packet)

    def recv(self, timeout: Optional[float] = 1 / MAX_SEND_RATE) -> Optional[HUDPPacket]:
        """Receive data from ready queue"""
        try:
            packet = self.ready_queue.get(timeout=timeout)
            return packet
        except queue.Empty:
            return None
    
    def close(self):
        """Stop receiver thread"""
        self.shutdown_event.set()
        if self.receiver_thread.is_alive():
            self.receiver_thread.join()


class SelectiveRepeatBuffer:
    """Buffer for reordering reliable packets using Selective Repeat"""
    
    def __init__(self, window_size: int, ready_queue: queue.Queue, skip_threshold: float = 0.2):
        self.window_size = window_size
        self.rcv_base = 0  # Next expected sequence number
        self.buffer: Dict[int, HUDPPacket] = {} # seq_num -> packet
        self.ready_queue: queue.Queue[HUDPPacket] = ready_queue
        self.skip_threshold = skip_threshold
    
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
            # Detect reordering (packet arrived after a higher seq packet)
            if seq > self.rcv_base:
                print(f"[Receiver] Detected reordering: received seq {seq} while waiting for {self.rcv_base}")
        
        self._deliver_ready_packets()
        self._check_skip_missing_packets()
        
        return True
    
    def _deliver_ready_packets(self):
        """Deliver all consecutive packets from rcv_base"""
        while self.rcv_base in self.buffer:
            packet = self.buffer.pop(self.rcv_base)
            self.ready_queue.put(packet)
            self.rcv_base += 1
            
    
    def _check_skip_missing_packets(self):
        """Skip missing packets if they exceed the threshold"""
        if self.rcv_base not in self.buffer:
            # Find next available packet
            higher_seqs = [s for s in self.buffer.keys() if s > self.rcv_base]
            if higher_seqs:
                next_seq = min(higher_seqs)
                packet = self.buffer.get(next_seq)
                # If more than skip_threshold time has passed since a packet with seq > rcv_base was sent,
                # more than skip_threshold time must have passed since packet with seq = rcv_base was FIRST sent
                if (time.time() - packet.timestamp) >= self.skip_threshold:
                    print(f"[Receiver] Skipping RELIABLE seq {self.rcv_base}")
                    self.buffer.pop(self.rcv_base)
                    self.rcv_base += 1
                    # Recursively deliver and check for more skips
                    self._deliver_ready_packets()
                    self._check_skip_missing_packets()