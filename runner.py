import argparse
import threading
import time
from typing import Dict, Any

from gameNetAPI import GameNetAPI
from sender_app import generate_mock_game_data

DONE_MESSAGE = b"__HUDP_DONE__"


def sender_worker(
    local_port: int,
    remote_port: int,
    duration: float,
    rate: float,
    ready_event: threading.Event,
    stop_event: threading.Event,
    results: Dict[str, Any],
) -> None:
    """Send mock packets until duration elapses, then emit a done control packet."""
    ready_event.wait()

    api = GameNetAPI(("0.0.0.0", local_port), ("127.0.0.1", remote_port))
    interval = 1.0 / rate if rate > 0 else 0.0
    start_time = time.time()
    end_time = start_time + duration
    packet_id = 0

    try:
        while time.time() < end_time and not stop_event.is_set():
            is_reliable = (packet_id % 2) == 0  # deterministic mix for repeatability
            payload = generate_mock_game_data(packet_id, is_reliable).encode()
            api.send(payload, reliable=is_reliable)
            packet_id += 1

            if interval > 0:
                sleep_until = start_time + packet_id * interval
                time_to_wait = sleep_until - time.time()
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

        # Let the receiver know we are finished.
        api.send(DONE_MESSAGE, reliable=True)
        stop_event.set()
    finally:
        elapsed = time.time() - start_time
        results["sender"] = {
            "sent_reliable": api.sent_reliable,
            "sent_unreliable": api.sent_unreliable,
            "duration": elapsed,
        }
        api.close()


def receiver_worker(
    local_port: int,
    remote_port: int,
    duration: float,
    buffer_time: float,
    ready_event: threading.Event,
    stop_event: threading.Event,
    results: Dict[str, Any],
) -> None:
    """Receive packets until told to stop or the extended window elapses."""
    api = GameNetAPI(("0.0.0.0", local_port), ("127.0.0.1", remote_port))
    ready_event.set()

    start_time = time.time()
    end_time = start_time + duration + buffer_time

    try:
        while time.time() < end_time and not stop_event.is_set():
            packet = api.recv(timeout=0.05)
            if packet and packet.payload == DONE_MESSAGE:
                stop_event.set()
    finally:
        elapsed = time.time() - start_time
        reliable_latencies = list(api.reliable_latencies)
        unreliable_latencies = list(api.unreliable_latencies)
        results["receiver"] = {
            "received_reliable": len(reliable_latencies),
            "received_unreliable": len(unreliable_latencies),
            "reliable_bytes": api.reliable_bytes_received,
            "unreliable_bytes": api.unreliable_bytes_received,
            "avg_reliable_latency_ms": (
                sum(reliable_latencies) / len(reliable_latencies) if reliable_latencies else None
            ),
            "avg_unreliable_latency_ms": (
                sum(unreliable_latencies) / len(unreliable_latencies) if unreliable_latencies else None
            ),
            "reliable_jitter_ms": api.reliable_jitter,
            "unreliable_jitter_ms": api.unreliable_jitter,
            "duration": elapsed,
        }
        api.close()


def compute_channel_metrics(
    sender_stats: Dict[str, Any], receiver_stats: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Compute per-channel delivery, latency, jitter, and throughput metrics."""
    duration = receiver_stats.get("duration", 0.0)

    def channel_summary(channel: str) -> Dict[str, Any]:
        sent = sender_stats.get(f"sent_{channel}", 0)
        received = receiver_stats.get(f"received_{channel}", 0)
        lost = max(0, sent - received)
        bytes_rcv = receiver_stats.get(f"{channel}_bytes", 0)
        throughput = (bytes_rcv / duration) if duration > 0 else 0.0
        delivery_ratio = (received / sent * 100.0) if sent > 0 else None
        avg_latency = receiver_stats.get(f"avg_{channel}_latency_ms")
        jitter = receiver_stats.get(f"{channel}_jitter_ms")

        return {
            "packets_sent": sent,
            "packets_received": received,
            "packets_lost": lost,
            "delivery_ratio_pct": delivery_ratio,
            "bytes_received": bytes_rcv,
            "throughput_bytes_per_sec": throughput,
            "avg_latency_ms": avg_latency,
            "jitter_ms": jitter,
        }

    return {
        "reliable": channel_summary("reliable"),
        "unreliable": channel_summary("unreliable"),
        "duration": duration,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local runner for sender/receiver apps.")
    parser.add_argument("--sender-port", type=int, default=10000, help="Local port for sender.")
    parser.add_argument("--receiver-port", type=int, default=10001, help="Local port for receiver.")
    parser.add_argument("--duration", type=float, default=5.0, help="Active send duration in seconds.")
    parser.add_argument("--rate", type=float, default=20.0, help="Packets per second for the sender.")
    parser.add_argument(
        "--receiver-buffer",
        type=float,
        default=1.0,
        help="Extra time (seconds) the receiver listens after sender stops.",
    )
    args = parser.parse_args()

    ready_event = threading.Event()
    stop_event = threading.Event()
    results: Dict[str, Any] = {}

    receiver_thread = threading.Thread(
        target=receiver_worker,
        args=(
            args.receiver_port,
            args.sender_port,
            args.duration,
            args.receiver_buffer,
            ready_event,
            stop_event,
            results,
        ),
        name="ReceiverThread",
    )
    sender_thread = threading.Thread(
        target=sender_worker,
        args=(
            args.sender_port,
            args.receiver_port,
            args.duration,
            args.rate,
            ready_event,
            stop_event,
            results,
        ),
        name="SenderThread",
    )

    receiver_thread.start()
    sender_thread.start()

    sender_thread.join()
    stop_event.set()
    receiver_thread.join()

    sender_stats = results.get("sender", {})
    receiver_stats = results.get("receiver", {})
    metrics = compute_channel_metrics(sender_stats, receiver_stats)

    def fmt_ms(value: Any) -> str:
        """Format millisecond values with 2 decimal places."""
        return f"{value:.2f} ms" if value is not None else "N/A"

    def fmt_ratio(value: Any) -> str:
        """Format percentage values with 2 decimal places."""
        return f"{value:.2f}%" if value is not None else "N/A"

    def fmt_throughput(value: float) -> str:
        """Format throughput in bytes per second."""
        return f"{value:.2f} B/s"

    print("\n" + "=" * 60)
    print("H-UDP CHANNEL PERFORMANCE")
    print("=" * 60)
    print(f"Send rate:          {args.rate:.1f} packets/s")
    print(f"Send duration:      {args.duration:.2f}s")

    for channel_name, label in [("reliable", "RELIABLE"), ("unreliable", "UNRELIABLE")]:
        channel = metrics[channel_name]
        print(f"\n{label} CHANNEL")
        print("-" * 60)
        print(f"  Latency:                   {fmt_ms(channel['avg_latency_ms'])}")
        print(f"  Jitter:                    {fmt_ms(channel['jitter_ms'])}\n")
        print(f"  Packets sent:              {channel['packets_sent']}")
        print(f"  Packets received:          {channel['packets_received']}")
        print(f"  Packet delivery ratio:     {fmt_ratio(channel['delivery_ratio_pct'])}\n")
        print(f"  Bytes received:            {channel['bytes_received']}")
        print(f"  Throughput:                {fmt_throughput(channel['throughput_bytes_per_sec'])} ({channel['bytes_received']} bytes / {metrics['duration']:.2f}s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
