from ring_doorbell import Ring
import json

#pip install ring_doorbell


PASSWORD = "replaced_from_secret_box"
with open('/gits/igor2/secretBox.json') as json_data:
    secrets = json.load(json_data)
    password = secrets["RingAccountPassword"]

ring = Ring('idvorkin@gmail.com', PASSWORD)

print(f"Connected Success:{ring.is_connected}")
doorbell = ring.doorbells[0]
print(doorbell)
