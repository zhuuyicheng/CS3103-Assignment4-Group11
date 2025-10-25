import time
import argparse
from gameNetAPI import GameNetAPI


def main(local_port: int, remote_port: int, duration: float):
    """Receiver application that displays received packets with detailed logs"""
    local_addr = ('0.0.0.0', local_port)
    remote_addr = ('127.0.0.1', remote_port)
    
    print(f"[Receiver] Starting on port {local_port}, expecting from port {remote_port}")
    print(f"[Receiver] Will run for {duration}s")
    print()
    
    api = GameNetAPI(local_addr, remote_addr)
    
    end_time = time.time() + duration
    reliable_count = 0
    unreliable_count = 0
    
    try:
        while time.time() < end_time:
            # Try receiving from reliable channel
            pkt = api.recv_reliable(timeout=0.05)
            if pkt:
                arrival_time = time.time()
                latency_ms = (arrival_time - pkt.timestamp) * 1000
                reliable_count += 1
                print(f"[Receiver] RELIABLE seq={pkt.seq_num}, arrival={arrival_time:.3f}, "
                      f"latency={latency_ms:.1f} ms, payload={pkt.payload.decode()}")
            
            # Try receiving from unreliable channel
            pkt = api.recv_unreliable(timeout=0.0)
            if pkt:
                arrival_time = time.time()
                latency_ms = (arrival_time - pkt.timestamp) * 1000
                unreliable_count += 1
                print(f"[Receiver] UNRELIABLE seq={pkt.seq_num}, arrival={arrival_time:.3f}, "
                      f"latency={latency_ms:.1f} ms, payload={pkt.payload.decode()}")
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n[Receiver] Interrupted by user")
    finally:
        skipped_count = api.get_skipped_count()
        print()
        print(f"[Receiver] Received {reliable_count} reliable packets")
        print(f"[Receiver] Received {unreliable_count} unreliable packets")
        print(f"[Receiver] Skipped {skipped_count} reliable packets")
        print(f"[Receiver] Total: {reliable_count + unreliable_count} packets")
        api.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-UDP Receiver Application')
    parser.add_argument('--local-port', type=int, default=10001, help='Local port')
    parser.add_argument('--remote-port', type=int, default=10000, help='Remote port')
    parser.add_argument('--duration', type=float, default=15.0, help='Test duration in seconds')
    args = parser.parse_args()
    
    main(args.local_port, args.remote_port, args.duration)
