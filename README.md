# CS3103-Assignment4-Group11

Adaptive Hybrid Transport Protocol for Games

Test with:

1. Open one terminal and type: python receiver_app.py --duration 6
2. On another terminal, immediately type: python sender_app.py --duration 5

Alternatively:
1. Run `python runner.py` (default duration is 5 seconds, and default packet rate is 20 packets per second)
2. You can customize the duration and packet rate using the `--duration` and `--rate` arguments respectively.

## GameNetAPI Specification
GameNetAPI provides a simplified interface for game networking with reliable and unreliable channels over UDP.

### Constructor
```python
GameNetAPI(local_addr: Tuple[str, int], remote_addr: Tuple[str, int])
```
- **local_addr**: Address to bind socket (IP, port)
- **remote_addr**: Destination address for sending packets

### Methods

#### send(payload: bytes, reliable: bool = False) -> int
Sends data on either channel.
- **payload**: Data to send (bytes)
- **reliable**: True for reliable channel, False for unreliable
- **Returns**: Sequence number

#### recv(timeout: Optional[float] = 0.01) -> Optional[HUDPPacket]
Receives packet from either channel.
- **timeout**: Max wait time in seconds
- **Returns**: HUDPPacket or None

#### display_metrics(duration: float)
Displays collected statistics (packets, throughput, latency, jitter).
- **duration**: Duration of the experiment in seconds

#### close()
Cleanup and shutdown sender/receiver threads.