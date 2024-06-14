import time
import threading

def main():
	print("Start")
	message : str= input("")
	for i in range(6):
		data : str= input("")
		time.sleep(0.1)
		if data.isnumeric():
			print(int(data)*i)

t = threading.Thread(target=main)
t.start()
t.join()
exit(int(t.is_alive()))