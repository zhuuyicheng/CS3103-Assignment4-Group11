import time
import random
import argparse
import json
from gameNetAPI import GameNetAPI

def generate_mock_game_data(packet_id: int, is_reliable: bool) -> str:
    """Generate mock game data based on packet type"""
    if is_reliable:
        # Reliable packets: critical game events
        event_type = random.choice(['join', 'score', 'level', 'item'])
        if event_type == 'join':
            return json.dumps({"join": packet_id, "name": f"P{packet_id % 10}"})
        elif event_type == 'score':
            return json.dumps({"score": random.randint(0, 999)})
        elif event_type == 'level':
            return json.dumps({"level": packet_id % 5 + 1})
        else:  # item
            return json.dumps({"item": random.choice(["coin", "gem", "key"]), "val": random.randint(10, 50)})
    else:
        # Unreliable packets: frequent position/state updates
        update_type = random.choice(['pos', 'vel', 'rot', 'anim'])
        if update_type == 'pos':
            return json.dumps({"x": random.randint(0, 800), "y": random.randint(0, 600)})
        elif update_type == 'vel':
            return json.dumps({"vx": random.randint(-50, 50), "vy": random.randint(-50, 50)})
        elif update_type == 'rot':
            return json.dumps({"angle": random.randint(0, 360)})
        else:  # anim
            return json.dumps({"frame": packet_id % 8, "state": random.choice(["idle", "run", "jump"])})

def main(local_port: int, remote_port: int, duration: float, rate: float):
    """Sender application that sends random reliable/unreliable game packets"""
    local_addr = ('0.0.0.0', local_port)
    remote_addr = ('127.0.0.1', remote_port)
    
    print(f"[Sender app] Starting on port {local_port}, sending to port {remote_port}")
    print(f"[Sender app] Duration: {duration}s, Rate: {rate} pps")
    print()
    
    api = GameNetAPI(local_addr, remote_addr)
    
    interval = 1.0 / rate
    end_time = time.time() + duration
    packet_id = 0
    
    try:
        while time.time() < end_time:
            # Randomly choose reliable or unreliable (50/50)
            is_reliable = random.choice([True, False])          
            mock_data = generate_mock_game_data(packet_id, is_reliable)
            payload = mock_data.encode()
            api.send(payload, reliable=is_reliable)
            packet_id += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[Sender app] Interrupted by user")
    finally:
        api.close()
        api.display_metrics(duration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-UDP Sender Application')
    parser.add_argument('--local-port', type=int, default=10000, help='Local port')
    parser.add_argument('--remote-port', type=int, default=10001, help='Remote port')
    parser.add_argument('--duration', type=float, default=10.0, help='Test duration in seconds')
    parser.add_argument('--rate', type=float, default=20.0, help='Packets per second')
    args = parser.parse_args()
    
    main(args.local_port, args.remote_port, args.duration, args.rate)
