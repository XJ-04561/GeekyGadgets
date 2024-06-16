
import threading
from time import sleep

def main():
	print("Start")
	for i in range(6):
		sleep(0.2)
		print(i)

t = threading.Thread(target=main)
t.start()
t.join()
exit(int(t.is_alive()))