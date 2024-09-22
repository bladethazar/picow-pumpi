import uasyncio
from picow_pumpi import PicoWPumPi

def main():
    pumpi = PicoWPumPi()
    uasyncio.run(pumpi.run())

if __name__ == "__main__":
    main()