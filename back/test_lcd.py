import smbus
from klasses.klasse_I2C import I2C

eersteLijn = 0x80  # LCD RAM address for the 1st line
tweedeLijn = 0xC0  # LCD RAM address for the 2nd line

i2c = I2C

# Open I2C interface
bus = smbus.SMBus(1)

i2c.__init__(i2c)
i2c.stuur_bericht(i2c,"ok",eersteLijn)

