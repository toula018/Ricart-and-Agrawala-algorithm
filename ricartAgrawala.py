import socket
import threading
import time


process_id = int(input('Enter the process ID: '))
process_port = int(input('Enter the process port: '))
SIZE = 1024

NUM_PROCESSES = 4
PORTS = [8001, 8002, 8003, 8004]
clock = 0
request_queue = []
num_replies = 0

MSG_REQUEST = "request"
MSG_REPLY = "reply"
MSG_RELEASE = "release"
demand_clock=0

FORMAT = "utf-8"

def requesting(process_id):
  while True:
    global clock, request_queue, replies_received, num_replies,demandeur,demand_clock
    demandeur = False
    while not demandeur:
        
        command=input("\nEnter a command (r to request access, q to quit) :  ")
        if command == 'r':
           print("Waiting for receiving permissions ", end="")
           for i in range(3):
             time.sleep(1.5) 
             print(".", end="", flush=True) 
           demandeur=True
        print("\n")

    clock += 1
    demand_clock=clock
    
    for i in range(NUM_PROCESSES):
        s=i+1
        if s != process_id:
            msg = f'{clock},{MSG_REQUEST},{process_id} '
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", PORTS[i]))
            sock.sendall(msg.encode(FORMAT))
          
            
            sock.close()

    while num_replies < NUM_PROCESSES - 1:
      time.sleep(0.1)
    
    print(f"\nProcess ({process_id}) entering --cs--")
    time.sleep(20)
    print(f"\nProcess ({process_id}) leaving --cs--")

    demandeur = False

    for i in range(NUM_PROCESSES):
        s=i+1
        if s != process_id:
            msg = f'{clock},{MSG_RELEASE},{process_id} '
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", PORTS[i]))
            sock.sendall(msg.encode(FORMAT))
    if request_queue:
     for i in range(len(request_queue)):
        req_id=request_queue[i]-1
        req_port = PORTS[req_id]

        msg = f'{clock},{MSG_REPLY},{process_id} '
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1",req_port))
        sock.send(msg.encode(FORMAT))
        sock.close()
       # print(f"\nyou gave permission to process {request_queue[i]} for entering critical section\n")
    request_queue = []
    num_replies = 0
    

def permission(conn):
    global clock, request_queue, replies_received, num_replies, in_cs
    msg=conn.recv(SIZE).decode(FORMAT)
    parts = msg.split(',')
    msg_clock = int(parts[0])
    msg_type = parts[1]
    msg_sender = int(parts[2])

    if msg_type == "request":

      clock = max(clock, msg_clock) 
      if demandeur == False or (demandeur == True and (msg_clock) < (clock)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", PORTS[msg_sender-1]))
            msg = f'{clock},{MSG_REPLY},{process_id} '
            sock.send(msg.encode(FORMAT))
           # print(f"\nyou gave the permission to process {msg_sender} for entering critical section")
      else:
            request_queue.append(msg_sender)
    elif msg_type == "reply":
        print(f"\nprocess ({ msg_sender}) gave you permission !\n")
        num_replies += 1
    else: 
        print(f"\nProcess ({msg_sender}) leaving --cs-- and released the resource\n")
       


       




def request_accept(process_port):
    per = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    per.bind(("127.0.0.1", process_port))
    per.listen()

    while True:
        conn,addr = per.accept()
        thread = threading.Thread(target = permission ,args=(conn,) )
        thread.start()
        


if __name__ == '__main__':
    req = threading.Thread(target = requesting ,args=(process_id,))
    req.start()
    per = threading.Thread(target = request_accept ,args=( process_port,))
    per.start()
    



