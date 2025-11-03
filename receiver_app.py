import time
import argparse
from gameNetAPI import GameNetAPI

def main(local_port: int, remote_port: int, duration: float):
    """Receiver application that displays received packets with detailed logs"""
    local_addr = ('0.0.0.0', local_port)
    remote_addr = ('127.0.0.1', remote_port)
    
    print(f"[Receiver app] Starting on port {local_port}, expecting from port {remote_port}")
    print(f"[Receiver app] Duration: {duration}s")
    print()
    
    api = GameNetAPI(local_addr, remote_addr)
    end_time = time.time() + duration
    
    try:
        while time.time() < end_time:
            # Try receiving from reliable channel
            api.recv()
    except KeyboardInterrupt:
        print("\n[Receiver app] Interrupted by user")
    finally:
        api.close()
        api.display_metrics(duration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-UDP Receiver Application')
    parser.add_argument('--local-port', type=int, default=10001, help='Local port')
    parser.add_argument('--remote-port', type=int, default=10000, help='Remote port')
    parser.add_argument('--duration', type=float, default=15.0, help='Test duration in seconds')
    args = parser.parse_args()
    
    main(args.local_port, args.remote_port, args.duration)
