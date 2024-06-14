
import threading

def main():
	print("Start")
	for i in range(6):
		print(i)

t = threading.Thread(target=main)
t.start()
t.join()
exit(int(t.is_alive()))