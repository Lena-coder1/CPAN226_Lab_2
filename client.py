# This program was modified by [Lena Mukhtar] / [n00639928]

import socket
import argparse
import time
import os

def run_client(target_ip, target_port, input_file):
    # 1. Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (target_ip, target_port)
    sock.settimeout(1.0)
    seq = 0 

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            while True:
                # Read a chunk of the file
                chunk = f.read(4096) # 4KB chunks
                
                if not chunk:
                    # End of file reached
                    break
                packet = f"{seq}|".encode() + chunk
                # Send the chunk
                while True:
                    sock.sendto(chunk, server_address)
                    print(f"[*] sent packet {seq}")

                    try: 
                        ack,_ =sock.recvfrom(1024)
                        ack_type,ack_seq = ack.decode().split("|")

                        if ack_type == "ACK" and int(ack_seq) == seq:
                            print(f"[+] ACK received for packet {seq}")
                            seq += 1
                            break 
                    except socket.timeout:
                        print(f"[!] Timeout , retransmitting packet {seq}")  
                 # Send empty packet to signal "End of File"
                eof_packet = f"{seq} |EOF".encode()
                sock.sendto(eof_packet, server_address)
                print("[*] File transmission complete.")   
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)