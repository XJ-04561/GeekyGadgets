import time
import threading

def main():
	print("Start")
	for i in range(6):
		data : str= input("")
		time.sleep(0.5)
		if data.isnumeric():
			print(int(data)*i)

t = threading.Thread(target=main)
t.start()
t.join(10)
exit(int(t.is_alive()))