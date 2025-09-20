#!/usr/bin/env python3
'''

The Sever Team

Names: Zavier Chambers, 
Mapping Of Opcodes
   [100]              # QUEUE
   [101]              # LEAVE
   [anything_else...] # send whatever data you want  only if in a room
 Server->Client:
   [110, "<room_id>", 0|1]  # MATCHED
   [111]                    # PERSON_LEFT
   [120, error_code, "<message>"]  # ERROR
'''
import sys, socket, threading, json, select, uuid
from queue import Queue
from contextlib import closing

# Opcodes
OP_QUEUE   = 100
OP_LEAVE   = 101
OP_MATCHED = 110
OP_PEERLEFT= 111
OP_ERROR   = 120

waiting = Queue()   # sockets waiting to be matched

def send_json(sock, arr):
    try:
        sock.sendall((json.dumps(arr) + "\n").encode("utf-8"))
    except Exception:
        pass

def relay_room(a, b):
    """ THIS IS WHERE MY DATA IS SENT <--- I am sending "newline terminated" lists exactly how you give them to the server between two sockets."""
    try:
        sockets = [a, b]
        while True:
            r, _, _ = select.select(sockets, [], [])
            for s in r:
                try:
                    data = s.recv(4096)
                except Exception:
                    data = b""
                if not data:
                    # disconnect
                    other = b if s is a else a
                    send_json(other, [OP_PEERLEFT])
                    return

                # Split by newline and the new forward complete lines
                lines = data.split(b"\n")
                for line in lines[:-1]:
                    msg = line.strip()
                    if not msg:
                        continue
                    # I dont know if this is the best way but I check for LEAVE inside room
                    try:
                        parsed = json.loads(msg.decode("utf-8"))
                    except Exception:
                        parsed = None
                    if parsed == [OP_LEAVE]:
                        other = b if s is a else a
                        send_json(other, [OP_PEERLEFT])
                        return

                    other = b if s is a else a
                    try:
                        other.sendall(msg + b"\n")
                    except Exception:
                        return
                
                # Clients should send newline-terminated JSON lists!!!
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass

def handle_client(conn):
    """Pre-match: only accept [100] (QUEUE) or [101] (LEAVE)."""
    with closing(conn):
        f = conn.makefile("r", encoding="utf-8", newline="\n")
        while True:
            line = f.readline()
            if not line:
                return  # disconnected before queueing
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                # Bad JSON before room -> error but keep reading
                send_json(conn, [OP_ERROR, 1, "Bad JSON; send a list like [100]."])
                continue
            if not isinstance(msg, list):
                send_json(conn, [OP_ERROR, 2, "Top level must be a list."])
                continue

            if msg == [OP_QUEUE]:
                waiting.put(conn)
                return
            elif msg == [OP_LEAVE]:
                # Not queued yet
                return
            else:
                # ONLY QUEUE/LEAVE allowed!!!!!
                send_json(conn, [OP_ERROR, 3, "Must [100] (QUEUE) before sending data."])

def accept_loop(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ls:
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind((host, port))
        ls.listen()
        print(f"Listening on {(host, port)}")

        # Matchmaker: every time two clients are queued, pair them
        def matchmaker():
            while True:
                a = waiting.get()
                b = waiting.get()
                room_id = str(uuid.uuid4())
                # Tell both clients they’ve been matched; role: 0 for first & 1 for second
                send_json(a, [OP_MATCHED, room_id, 0])
                send_json(b, [OP_MATCHED, room_id, 1])
              # HAD TO LEARN THREADING FOR THIS PART!
                threading.Thread(target=relay_room, args=(a, b), daemon=True).start()

        threading.Thread(target=matchmaker, daemon=True).start()

        while True:
            conn, _ = ls.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
# I hope everyone is okay with this easy to apply in the labs style of using a script. I DO THIS AT MY JOB!
def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(2)
    host, port = sys.argv[1], int(sys.argv[2])
    accept_loop(host, port)

if __name__ == "__main__":
    main()
