import time
import argparse
from gameNetAPI import GameNetAPI
from packet import CHANNEL_RELIABLE, CHANNEL_UNRELIABLE


def main(local_port: int, remote_port: int, duration: float):
    """Receiver application that displays received packets with detailed logs"""
    local_addr = ('0.0.0.0', local_port)
    remote_addr = ('127.0.0.1', remote_port)
    
    print(f"[Receiver app] Starting on port {local_port}, expecting from port {remote_port}")
    print(f"[Receiver app] Duration: {duration}s")
    print()
    
    api = GameNetAPI(local_addr, remote_addr)
    
    end_time = time.time() + duration
    reliable_pkts_received = 0
    reliable_bytes_received = 0
    unreliable_pkts_received = 0
    unreliable_bytes_received = 0
    
    try:
        while time.time() < end_time:
            # Try receiving from reliable channel
            pkt = api.recv()
            if pkt:
                latency_ms = (time.time() - pkt.timestamp) * 1000

                if pkt.channel_type ==  CHANNEL_RELIABLE:
                    print(f"[Receiver app] Received RELIABLE seq={pkt.seq_num}, latency={latency_ms:.1f} ms")
                    reliable_pkts_received += 1
                    reliable_bytes_received += len(pkt.payload)
                elif pkt.channel_type ==  CHANNEL_UNRELIABLE:
                    print(f"[Receiver app] Received UNRELIABLE seq={pkt.seq_num}, latency={latency_ms:.1f} ms")
                    unreliable_pkts_received += 1
                    unreliable_bytes_received += len(pkt.payload)
    
    except KeyboardInterrupt:
        print("\n[Receiver app] Interrupted by user")
    finally:
        print()
        print(f"[Receiver app] RELIABLE: Packets received = {reliable_pkts_received}, throughput = {(reliable_bytes_received / duration):.2f} bytes/s")
        print(f"[Receiver app] UNRELIABLE: Packets received = {unreliable_pkts_received}, throughput = {(unreliable_bytes_received / duration):.2f} bytes/s")
        api.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-UDP Receiver Application')
    parser.add_argument('--local-port', type=int, default=10001, help='Local port')
    parser.add_argument('--remote-port', type=int, default=10000, help='Remote port')
    parser.add_argument('--duration', type=float, default=15.0, help='Test duration in seconds')
    args = parser.parse_args()
    
    main(args.local_port, args.remote_port, args.duration)
