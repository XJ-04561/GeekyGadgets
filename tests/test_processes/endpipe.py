
import threading
from time import sleep

def main():
	print("Start")
	message : str= input("")
	for i in range(6):
		data : str= input("")
		if data.isnumeric():
			print(int(data)*i)

t = threading.Thread(target=main)
t.start()
t.join(10)
exit(int(t.is_alive()))