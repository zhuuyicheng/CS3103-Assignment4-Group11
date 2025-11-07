import socket
import time
import threading
from typing import Dict, Tuple
from packet import HUDPPacket, CHANNEL_RELIABLE, CHANNEL_UNRELIABLE, MAX_PAYLOAD_SIZE, MAX_PACKET_SIZE

WINDOW_SIZE = 32
TIMEOUT = 0.2  # 200ms
MAX_RETRIES = 5
MAX_SEND_RATE = 100  # packets per second

class HUDPSender:
    """H-UDP sender with reliable and unreliable channels"""
    
    def __init__(self, sock: socket.socket, dest_addr: Tuple[str, int]):
        self.sock = sock
        self.dest_addr = dest_addr
        self.unreliable_seq = 0
        
        # Reliable channel state
        self.send_base = 0 # Earliest packet sent but not yet acknowledged
        self.next_seq = 0 
        self.window: Dict[int, Tuple[HUDPPacket, int]] = {}  # seq -> (packet, retries)
        self.lock = threading.Lock() # Lock for send_base, next_seq, and window
        self.condition = threading.Condition(self.lock)
        
        self.shutdown_event = threading.Event()
        # A daemon thread is a background thread that will automatically terminate when the main program exits, 
        # regardless of whether the daemon thread has completed its task
        self.ack_thread = threading.Thread(target=self._ack_receiver, daemon=True)
        self.ack_thread.start()
    
        self.timer_thread = threading.Thread(target=self._retransmit_timer, daemon=True)
        self.timer_thread.start()
    
    def send_unreliable(self, data: bytes) -> int:
        """Send data on unreliable channel (fire and forget)"""
        if len(data) > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload too large: {len(data)} > {MAX_PAYLOAD_SIZE}")
        
        seq = self.unreliable_seq
        packet = HUDPPacket(
            channel_type=CHANNEL_UNRELIABLE,
            seq_num=seq,
            ack_num=0,
            timestamp=time.time(),
            payload=data
        )
        self.unreliable_seq += 1
        
        self.sock.sendto(packet.serialize(), self.dest_addr)
        return seq
    
    def send_reliable(self, data: bytes) -> int:
        """Send data on reliable channel with Selective Repeat"""
        with self.lock:
            # Wait if window is full
            while self.next_seq >= self.send_base + WINDOW_SIZE:
                # self.lock is released while waiting and re-acquired upon wake-up
                self.condition.wait()
            
            seq = self.next_seq
            packet = HUDPPacket(
                channel_type=CHANNEL_RELIABLE,
                seq_num=seq,
                ack_num=0,
                timestamp=time.time(),
                payload=data
            )
            
            # Send packet
            self.sock.sendto(packet.serialize(), self.dest_addr)
            
            # Add to window
            self.window[seq] = (packet, 0)
            self.next_seq += 1
        
        return seq
    
    def _ack_receiver(self):
        """Background thread to receive ACKs"""
        while not self.shutdown_event.is_set():
            try:
                self.sock.settimeout(1 / MAX_SEND_RATE) # Set timeout to periodically check self.shutdown_event
                data, _ = self.sock.recvfrom(MAX_PACKET_SIZE)
                packet = HUDPPacket.deserialize(data)
                
                if packet.channel_type == CHANNEL_RELIABLE:
                    self._handle_ack(packet.ack_num)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Sender] ACK receiver error: {e}")
    
    def _handle_ack(self, ack_num: int):
        """Process ACK and slide window"""
        with self.lock:
            # Remove ACKed packet from window
            if ack_num in self.window:
                _, retries = self.window[ack_num]
                print(f"[Sender] ACK received for RELIABLE seq={ack_num}, retries={retries}")
                del self.window[ack_num]
            
            # Slide window base
            while self.send_base not in self.window and self.send_base < self.next_seq:
                self.send_base += 1
            
            # Wake up waiting thread
            self.condition.notify() 

    def _retransmit_timer(self):
        """Background thread to retransmit timed-out packets"""
        # Instead of maintaining a timer for each unACKed packet,
        # we keep checking how long each unACKed packet has been waiting
        while not self.shutdown_event.is_set():
            with self.lock:
                for seq, (packet, retries) in list(self.window.items()):
                    if time.time() - packet.timestamp > TIMEOUT:
                        if retries >= MAX_RETRIES:
                            print(f"[Sender] Max retries reached for RELIABLE seq={seq}, dropping")
                            del self.window[seq]

                            # Slide window base
                            while self.send_base not in self.window and self.send_base < self.next_seq:
                                self.send_base += 1

                            # Wake up waiting thread
                            self.condition.notify() 
                        else:
                            # Retransmit
                            packet.timestamp = time.time()
                            self.sock.sendto(packet.serialize(), self.dest_addr)
                            self.window[seq] = (packet, retries + 1)
                            print(f"[Sender] Retransmitting RELIABLE seq={seq} (attempt {retries + 1})")

    def close(self):
        """Stop sender threads"""
        self.shutdown_event.set()
        if self.ack_thread.is_alive():
            self.ack_thread.join()
        if self.timer_thread.is_alive():
            self.timer_thread.join()