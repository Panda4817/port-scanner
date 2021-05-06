import threading
from queue import Queue
import time
import socket
from common_ports import ports_and_services

open_ports = []


def port_scan(host, port):
    global open_ports
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = s.connect_ex((host, port))
    if res == 0:
        open_ports.append(port)
    s.close()


def get_open_ports(target, port_range, verbose=False):
    print_lock = threading.Lock()
    global open_ports
    open_ports = []
    try:
        ip_addr = socket.gethostbyname(target)
    except Exception as e:
        try:
            parts = [int(p) for p in target.split(".")]
            return "Error: Invalid IP address"
        except:
            return "Error: Invalid hostname"

    # Create the queue and threader
    q = Queue()

    def threader():
        while True:
            # gets an worker from the queue
            host, port = q.get()

            # Run the example job with the avail worker in queue (thread)
            port_scan(host, port)

            # completed with the job
            q.task_done()

    # how many threads are we going to allow for
    for x in range(1000):
        t = threading.Thread(target=threader)

        # classifying as a daemon, so they will die when the main dies
        t.daemon = True

        # begins, must come after daemon definition
        t.start()

    start = time.time()

    for port in range(port_range[0], port_range[1] + 1):
        q.put((ip_addr, port))

    # wait until the thread terminates.
    q.join()

    if verbose:
        if ip_addr != target:
            domain = target
        else:
            try:
                domain = socket.gethostbyaddr(ip_addr)[0]
            except:
                domain = None
        if domain:
            result = f"Open ports for {domain} ({ip_addr})\nPORT     SERVICE"
        else:
            result = f"Open ports for {ip_addr}\nPORT     SERVICE"

        for port in open_ports:
            spaces = (4 - len(str(port)) + 5) * " "
            try:
                result += f"\n{port}" + spaces + f"{ports_and_services[port]}"
            except KeyError:
                continue
        return result

    return(open_ports)
