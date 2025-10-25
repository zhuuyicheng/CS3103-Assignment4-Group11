import struct

HEADER_SIZE = 17  # 1 + 4 + 4 + 8 bytes
CHANNEL_RELIABLE = 0
CHANNEL_UNRELIABLE = 1
MAX_PACKET_SIZE = 1400 # Ensures that packet with IP and UDP header will not exceed MTU of 1500 bytes
MAX_PAYLOAD_SIZE = MAX_PACKET_SIZE - HEADER_SIZE

class HUDPPacket:
    """Represents an H-UDP packet with header and payload"""
    
    def __init__(self, channel_type: int, seq_num: int, ack_num: int, 
                 timestamp: float, payload: bytes):
        self.channel_type = channel_type
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.timestamp = timestamp
        self.payload = payload
    
    def serialize(self) -> bytes:
        """Serialize packet to bytes"""
        header = struct.pack('!BIId', 
                           self.channel_type,
                           self.seq_num,
                           self.ack_num,
                           self.timestamp)
        return header + self.payload
    
    @staticmethod
    def deserialize(data: bytes) -> 'HUDPPacket':
        """Deserialize bytes to packet"""
        if len(data) < HEADER_SIZE:
            raise ValueError("Invalid packet size")
        
        channel_type, seq_num, ack_num, timestamp = struct.unpack(
            '!BIId', data[:HEADER_SIZE])
        payload = data[HEADER_SIZE:]
        
        return HUDPPacket(channel_type, seq_num, ack_num, timestamp, payload)
