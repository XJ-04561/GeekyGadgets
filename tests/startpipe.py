import time
import threading

def main():
	print("Start")
	for i in range(6):
		time.sleep(0.5)
		print(i)

t = threading.Thread(target=main)
t.start()
t.join()
exit(int(t.is_alive()))