import paho.mqtt.client as mqtt
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message published")

def config_pn532():
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs_pin = DigitalInOut(board.D8)
    pn532 = PN532_SPI(spi, cs_pin, debug=False)
    pn532.SAM_configuration()
    return pn532

def read_block(pn532, uid, block_number):
    key_a = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    authenticated = pn532.mifare_classic_authenticate_block(uid=uid, block_number=block_number, key_number=0x60, key=key_a)

    # Read to ensure data was written
    block_data = pn532.mifare_classic_read_block(block_number)

    return authenticated, block_data[0] if authenticated and block_data is not None else None

# Initialize PN532
pn532 = config_pn532()

# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="ingenuin")
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to MQTT broker
try:
    client.connect("broker.hivemq.com", 1883, 60)
except Exception as e:
    print("Failed to connect to MQTT broker:", e)
    exit(1)

try:
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            authenticated, student_id = read_block(pn532, uid, 1)
            if authenticated and student_id is not None:
                print("Student ID:", student_id)
                # Publish student ID to MQTT topic
                try:
                    client.publish("student-id", payload=student_id)
                except Exception as e:
                    print("Failed to publish message to MQTT broker:", e)
        time.sleep(1)
except KeyboardInterrupt:
    print("Keyboard interrupt detected, disconnecting from MQTT broker...")
    client.disconnect()
    print("Disconnected from MQTT broker")
gi