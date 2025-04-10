import socket
import cv2
import os
import math
import threading
import queue
import time

def send_video(file_path, host, port):
    """Send video frames over a socket connection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)  # Reduce timeout for ACK

    cap = cv2.VideoCapture(file_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Set lower resolution
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get video frame rate
    frame_delay = 1 / fps if fps > 0 else 0.03  # Set frame delay, default ~30 FPS

    frame_queue = queue.Queue(maxsize=10)  # Queue for storing compressed frames

    def read_and_compress_frames():
        """Thread for reading and compressing video frames."""
        while True:
            ret, frame = cap.read()
            if not ret:
                frame_queue.put(None)  # Signal end of video
                break

            # Resize the frame to reduce size (optional)
            frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

            # Encode the frame as WebP
            _, buffer = cv2.imencode('.webp', frame, [cv2.IMWRITE_WEBP_QUALITY, 25])  # WebP compression
            frame_queue.put(buffer.tobytes())

    def transmit_frames():
        """Thread for transmitting video frames."""
        f_total_cnt = 0
        f_ack_cnt = 0

        while True:
            data = frame_queue.get()

            if data is None:
                break  # End signal, exit transmission thread
            
            f_total_cnt += 1

            # Send frame type indicator
            sock.sendto(b"FRAME", (host, port))

            # Split the data into chunks
            max_packet_size = 8000
            num_chunks = math.ceil(len(data) / max_packet_size)

            for i in range(num_chunks):
                chunk = data[i * max_packet_size:(i + 1) * max_packet_size]
                sock.sendto(chunk, (host, port))

            sock.sendto(b"END", (host, port))

            try:
                ack, _ = sock.recvfrom(1024)
                if ack != b"ACK":
                    print("Unexpected response %s, skipping frame..." % ack.decode('utf-8'))
                    continue
                else:
                    f_ack_cnt += 1
            except socket.timeout:
                print("ACK not received, skipping frame...")
                continue
                
        print(f"Total frames sent: {f_total_cnt}, ACK received: {f_ack_cnt}")
        print(f"ACK ratio: {f_ack_cnt / f_total_cnt:.2%}")

    # Start thread for reading and compressing frames
    reader_thread = threading.Thread(target=read_and_compress_frames, daemon=True)
    reader_thread.start()

    # Start thread for transmitting frames
    transmitter_thread = threading.Thread(target=transmit_frames, daemon=True)
    transmitter_thread.start()

    # Wait for threads to finish
    reader_thread.join()
    transmitter_thread.join()

    cap.release()
    sock.close()

if __name__ == "__main__":
    HOST = '192.168.50.85'  # Receiver's IP address
    PORT = 5000         # Receiver's port
    FILE_PATH = os.path.join(os.path.dirname(__file__), '../video/4250intro.mp4')  # Path to the video file

    send_video(FILE_PATH, HOST, PORT)