import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

try:
    print([hex(x) for x in i2c.scan()])
finally:
    i2c.unlock()
