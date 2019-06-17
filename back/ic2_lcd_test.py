import smbus
import time

I2C_adres = 0x3f #starting adres -> sudo i2cdetect -y 1
maxChar = 16 #max aantal characters

sturen_data = 1  # Mode - Sending data
sturen_command = 0  # Mode - Sending command

eersteLijn = 0x80  # LCD RAM address for the 1st line
tweedeLijn = 0xC0  # LCD RAM address for the 2nd line
lcd_achtergrond = 0x08  # aanzetten achtergrond licht
enable = 0b00000100  # Enable bit

# Open I2C interface
bus = smbus.SMBus(1)

def lcd_init():
    lcd_byte(0x33, sturen_command)  # 110011 initialiseren
    lcd_byte(0x32, sturen_command)  # 110010 initialiseren
    lcd_byte(0x01, sturen_command)  # 000001 Clear display
    time.sleep(0.005)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data,0 for command

    bits_high = mode | (bits & 0xF0) | lcd_achtergrond
    bits_low = mode | ((bits << 4) & 0xF0) | lcd_achtergrond

    # High bits
    bus.write_byte(I2C_adres, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_adres, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(0.005)
    bus.write_byte(I2C_adres, (bits | enable))
    time.sleep(0.005)
    bus.write_byte(I2C_adres, (bits & ~enable))
    time.sleep(0.005)

def stuur_bericht(bericht, lijn):
    # Send string to display

    bericht = bericht.ljust(maxChar, " ")

    lcd_byte(lijn, sturen_command)

    for i in range(maxChar):
        lcd_byte(ord(bericht[i]), sturen_data)

def main():
    # initialiseren display
    lcd_init()

    while True:
        # Send some test
        stuur_bericht("hello world", eersteLijn)
        stuur_bericht("tweede lijn", tweedeLijn)

        time.sleep(3)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, sturen_command)