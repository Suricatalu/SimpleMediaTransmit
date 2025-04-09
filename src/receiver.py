import socket
import cv2
import numpy as np

def receive_video(host='0.0.0.0', port=5000):
    """Receive video frames over a socket connection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print("Receiver is ready to receive video...")

    buffer = b''  # Buffer to store incoming data

    while True:
        try:
            data, addr = sock.recvfrom(8000)  # Adjusted maximum UDP packet size
            if not data:
                break

            # Check for frame type indicator
            if data == b"FRAME":
                continue

            # Check for end-of-frame marker
            if data == b"END":
                try:
                    # Convert byte array to numpy array
                    frame_array = np.frombuffer(buffer, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # Display the resulting frame
                        cv2.imshow('Rec', frame)

                        # Send ACK to transmitter
                        sock.sendto(b"ACK", addr)
                    else:
                        print("Error: Frame is None after decoding, skipping...")
                        # Send ACK even if the frame is None to avoid blocking the transmitter
                        sock.sendto(b"ACK", addr)
                except cv2.error as e:
                    print(f"Error decoding frame: {e}, skipping...")
                    # Send ACK even if decoding fails to avoid blocking the transmitter
                    sock.sendto(b"ACK", addr)

                # Reset buffer for the next frame
                buffer = b''
            else:
                # Append received chunk to buffer
                buffer += data

        except Exception as e:
            print(f"Error receiving data: {e}")
            break

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    sock.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    receive_video()