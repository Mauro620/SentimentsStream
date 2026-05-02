import os
import socket
import time
from csv import reader


def main() -> None:
    host: str = "0.0.0.0"
    port: int = int(os.getenv("SOCKET_PORT", "9999"))
    rate_hz: float = float(os.getenv("STREAM_RATE_HZ", "5.0"))
    loop: bool = os.getenv("STREAM_LOOP", "false").lower() == "true"
    csv_path: str = os.getenv("RAW_PATH", "data/raw/dataset_sentimientos_500.csv")
    delay: float = 1.0 / rate_hz

    def stream_data(conn: socket.socket) -> None:
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_reader = reader(f)
            next(csv_reader)  # skip header
            for row in csv_reader:
                if len(row) >= 2:
                    conn.sendall((row[0] + "\n").encode("utf-8"))
                    time.sleep(delay)

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(1)
            print(f"Listening on {host}:{port}...")

            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")
                try:
                    stream_data(conn)
                    print("Finished streaming CSV.")
                except BrokenPipeError:
                    print("Client disconnected.")
                except Exception as e:
                    print(f"Error: {e}")

        if not loop:
            break
        print("Looping... restarting server.")
        time.sleep(1)


if __name__ == "__main__":
    main()
