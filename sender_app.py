import time
import random
import argparse
from gameNetAPI import GameNetAPI


def main(local_port: int, remote_port: int, duration: float, rate: float):
    """Sender application that sends random reliable/unreliable game packets"""
    local_addr = ('0.0.0.0', local_port)
    remote_addr = ('127.0.0.1', remote_port)
    
    print(f"[Sender] Starting on port {local_port}, sending to port {remote_port}")
    print(f"[Sender] Duration: {duration}s, Rate: {rate} pps")
    
    api = GameNetAPI(local_addr, remote_addr)
    
    interval = 1.0 / rate
    end_time = time.time() + duration
    packet_id = 0
    reliable_count = 0
    unreliable_count = 0
    
    try:
        while time.time() < end_time:
            # Randomly choose reliable or unreliable (50/50)
            is_reliable = random.choice([True, False])
            
            if is_reliable:
                # Game state update (reliable)
                payload = f'{{"type":"game_state","id":{packet_id},"ts":{time.time():.3f}}}'.encode()
                seq = api.send(payload, reliable=True)
                print(f"[Sender] Sent RELIABLE seq={seq}, id={packet_id}, ts={time.time():.3f}")
                reliable_count += 1
            else:
                # Movement update (unreliable)
                payload = f'{{"type":"movement","id":{packet_id},"ts":{time.time():.3f}}}'.encode()
                seq = api.send(payload, reliable=False)
                print(f"[Sender] Sent UNRELIABLE seq={seq}, id={packet_id}, ts={time.time():.3f}")
                unreliable_count += 1
            
            packet_id += 1
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n[Sender] Interrupted by user")
    finally:
        api.close()
        print()
        print(f"[Sender] Sent {reliable_count} reliable packets")
        print(f"[Sender] Sent {unreliable_count} unreliable packets")
        print(f"[Sender] Total: {packet_id} packets")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-UDP Sender Application')
    parser.add_argument('--local-port', type=int, default=10000, help='Local port')
    parser.add_argument('--remote-port', type=int, default=10001, help='Remote port')
    parser.add_argument('--duration', type=float, default=10.0, help='Test duration in seconds')
    parser.add_argument('--rate', type=float, default=20.0, help='Packets per second')
    args = parser.parse_args()
    
    main(args.local_port, args.remote_port, args.duration, args.rate)
