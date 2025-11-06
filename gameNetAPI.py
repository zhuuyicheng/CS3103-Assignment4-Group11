import socket
from typing import Optional, Tuple
from packet import HUDPPacket
from sender import HUDPSender, MAX_SEND_RATE
from receiver import HUDPReceiver
import time
import logging
from packet import CHANNEL_RELIABLE, CHANNEL_UNRELIABLE

class GameNetAPI:
    """H-UDP API for game networking with reliable and unreliable channels"""
    
    def __init__(self, local_addr: Tuple[str, int], remote_addr: Tuple[str, int], threshold: float = 0.2):
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(local_addr)
        
        # Create sender and receiver (they will manage their own threads)
        self.sender = HUDPSender(self.sock, remote_addr)
        self.receiver = HUDPReceiver(self.sock, threshold)
        
        # Track packet statistics
        self.sent_reliable = 0
        self.sent_unreliable = 0
        self.reliable_bytes_received = 0
        self.unreliable_bytes_received = 0
        self.reliable_latencies = []
        self.unreliable_latencies = []
        # J(i) = J(i-1) + (|D(i-1,i)| - J(i-1))/16
        self.reliable_jitter = 0
        self.unreliable_jitter = 0

        logging.basicConfig(
            filename='log.log',  # Log file name
            filemode='a',  # Append mode ('w' would overwrite)
            format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
            level=logging.INFO
        )

        logging.info(f"API Starting")

    def send(self, payload: bytes, reliable: bool = False) -> int:
        """Send data on either reliable or unreliable channel"""
        if reliable:
            seq = self.sender.send_reliable(payload)
            self.sent_reliable += 1
            logging.info(f"[gameNetAPI] Sent RELIABLE seq={seq}")
            return seq
        else:
            seq = self.sender.send_unreliable(payload)
            self.sent_unreliable += 1
            logging.info(f"[gameNetAPI] Sent UNRELIABLE seq={seq}")
            return seq

    def recv(self, timeout: Optional[float] = 1 / MAX_SEND_RATE) -> Optional[HUDPPacket]:
        """Receive data from either channel"""
        packet = self.receiver.recv(timeout=timeout)
        if packet:
            latency_ms = (time.time() - packet.timestamp) * 1000
            if packet.channel_type == CHANNEL_RELIABLE:
                logging.info(f"[gameNetAPI] Received RELIABLE seq={packet.seq_num}, latency={latency_ms:.1f} ms")
                self.reliable_bytes_received += len(packet.payload)
                latency_diff = abs(latency_ms - self.reliable_latencies[-1] if self.reliable_latencies else 0)
                self.reliable_jitter = self.reliable_jitter + (latency_diff - self.reliable_jitter) / 16
                self.reliable_latencies.append(latency_ms)
            elif packet.channel_type == CHANNEL_UNRELIABLE:
                logging.info(f"[gameNetAPI] Received UNRELIABLE seq={packet.seq_num}, latency={latency_ms:.1f} ms")
                self.unreliable_bytes_received += len(packet.payload)
                latency_diff = abs(latency_ms - self.unreliable_latencies[-1] if self.unreliable_latencies else 0)
                self.unreliable_jitter = self.unreliable_jitter + (latency_diff - self.unreliable_jitter) / 16
                self.unreliable_latencies.append(latency_ms)
        return packet

    def display_metrics(self, duration: float):
        """Display collected metrics"""
        print()
        print(f"[gameNetAPI] SENT METRICS:")
        print(f"  RELIABLE: Packets sent = {self.sent_reliable}")
        print(f"  UNRELIABLE: Packets sent = {self.sent_unreliable}")
        print(f"[gameNetAPI] RECEIVED METRICS:")
        print(f"  RELIABLE: Packets received = {len(self.reliable_latencies)}, throughput = {(self.reliable_bytes_received / duration):.2f} bytes/s")
        if self.reliable_latencies:
            avg_reliable_latency = sum(self.reliable_latencies) / len(self.reliable_latencies)
            print(f"    Average latency = {avg_reliable_latency:.2f} ms")
        print(f"    Jitter = {self.reliable_jitter:.2f} ms")
        print(f"  UNRELIABLE: Packets received = {len(self.unreliable_latencies)}, throughput = {(self.unreliable_bytes_received / duration):.2f} bytes/s")
        if self.unreliable_latencies:
            avg_unreliable_latency = sum(self.unreliable_latencies) / len(self.unreliable_latencies)
            print(f"    Average latency = {avg_unreliable_latency:.2f} ms")
        print(f"    Jitter = {self.unreliable_jitter:.2f} ms")

    def close(self):
        """Close the API and cleanup resources"""
        self.sender.close()
        self.receiver.close()
        self.sock.close()
