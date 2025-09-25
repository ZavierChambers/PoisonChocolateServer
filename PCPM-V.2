#!/usr/bin/env python3
"""
The Server Team
Names: Zavier Chambers
Mapping Of Opcodes
   [100]              # QUEUE
   [101]              # LEAVE
   [anything_else...] # send whatever data you want only if in a room
Server->Client:
   [110, "<room_id>", 0|1]  # MATCHED
   [111]                    # PERSON_LEFT
   [120, error_code, "<message>"]  # ERROR
"""
import sys, socket, threading, json, select, uuid
from queue import Queue
import logging

# ---------- Logging Setup ----------
logging.basicConfig(
    level=logging.INFO,                          # INFO shows connections & normal flow
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
# -----------------------------------

# Opcodes
OP_QUEUE   = 100
OP_LEAVE   = 101
OP_MATCHED = 110
OP_PEERLEFT= 111
OP_ERROR   = 120

waiting = Queue()   # sockets waiting to be matched

def send_json(sock, arr):
    """Send a JSON list over the socket."""
    try:
        sock.sendall((json.dumps(arr) + "\n").encode("utf-8"))
        logging.debug(f"Sent to {sock.getpeername()}: {arr}")
    except Exception as e:
        logging.warning(f"Failed to send to client: {e}")

def relay_room(a, b):
    """
    Forward newline-terminated JSON lists between two sockets.
    """
    logging.info("Room relay started between %s and %s", a.getpeername(), b.getpeername())
    try:
        sockets = [a, b]
        while True:
            r, _, _ = select.select(sockets, [], [])
            for s in r:
                try:
                    data = s.recv(4096)
                except Exception as e:
                    logging.error(f"Receive error: {e}")
                    data = b""
                if not data:
                    other = b if s is a else a
                    logging.info("Client %s disconnected", s.getpeername())
                    send_json(other, [OP_PEERLEFT])
                    return

                # Split by newline and forward complete lines
                lines = data.split(b"\n")
                for line in lines[:-1]:
                    msg = line.strip()
                    if not msg:
                        continue
                    try:
                        parsed = json.loads(msg.decode("utf-8"))
                        logging.debug(f"Relaying message {parsed} from {s.getpeername()}")
                    except Exception:
                        parsed = None
                        logging.warning("Bad JSON received in room relay")

                    if parsed == [OP_LEAVE]:
                        other = b if s is a else a
                        logging.info("Client %s left room", s.getpeername())
                        send_json(other, [OP_PEERLEFT])
                        return

                    other = b if s is a else a
                    try:
                        other.sendall(msg + b"\n")
                    except Exception as e:
                        logging.error(f"Send error to {other.getpeername()}: {e}")
                        return
    finally:
        for sock in (a, b):
            try:
                sock.close()
            except:
                pass
        logging.info("Room relay ended")

def handle_client(conn):
    """Accept only [100] (QUEUE) or [101] (LEAVE) before matchmaking."""
    addr = conn.getpeername()
    logging.info("Handling client %s", addr)
    f = conn.makefile("r", encoding="utf-8", newline="\n")
    while True:
        line = f.readline()
        if not line:
            logging.info("Client %s disconnected before queueing", addr)
            return
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            logging.warning("Bad JSON from %s: %s", addr, line)
            send_json(conn, [OP_ERROR, 1, "Bad JSON; send a list like [100]."])
            continue
        if not isinstance(msg, list):
            logging.warning("Non-list message from %s: %s", addr, msg)
            send_json(conn, [OP_ERROR, 2, "Top level must be a list."])
            continue

        if msg == [OP_QUEUE]:
            logging.info("Client %s queued", addr)
            waiting.put(conn)
            break
        elif msg == [OP_LEAVE]:
            logging.info("Client %s left before queueing", addr)
            break
        else:
            logging.warning("Invalid pre-match message from %s: %s", addr, msg)
            send_json(conn, [OP_ERROR, 3, "Must [100] (QUEUE) before sending data."])

def accept_loop(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ls:
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind((host, port))
        ls.listen()
        logging.info("Server listening on %s:%d", host, port)

        # Matchmaker pairs queued clients
        def matchmaker():
            while True:
                a = waiting.get()
                b = waiting.get()
                room_id = str(uuid.uuid4())
                logging.info("Matched %s and %s into room %s", a.getpeername(), b.getpeername(), room_id)
                send_json(a, [OP_MATCHED, room_id, 0])
                send_json(b, [OP_MATCHED, room_id, 1])
                threading.Thread(target=relay_room, args=(a, b), daemon=True).start()

        threading.Thread(target=matchmaker, daemon=True).start()

        while True:
            conn, addr = ls.accept()
            logging.info("New connection from %s", addr)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(2)
    host, port = sys.argv[1], int(sys.argv[2])
    accept_loop(host, port)

if __name__ == "__main__":
    main()
