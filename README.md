# PicoW-PumPi: Advanced Plant Watering Control System

## Project Overview

PicoW-PumPi is a sophisticated plant watering control system designed to work in conjunction with the existing PicoW-Growmat environmental monitoring system. Built on the Raspberry Pi Pico W platform and utilizing MicroPython, this system manages water pumps and solenoid valves to provide intelligent watering control for multiple plants.

### Key Features

- Automated watering control based on soil moisture data received via MQTT
- Control of a main water pump and four solenoid valves for individual plant watering
- Management of a small oxygenation pump for the water tank
- Manual control options with individual switches for pump and valves
- MQTT integration for receiving moisture data and remote control
- Configurable settings via MQTT for easy customization
- Robust error handling and system health monitoring

## Hardware Components

- Raspberry Pi Pico W
- Water pump (submersible, suitable for a 10L tank)
- 4 x Solenoid valves
- Small oxygenation pump
- 5 x Switches (1 for main pump, 4 for individual valves)
- 10L Water tank
- Appropriate power supply for pumps and valves

## Software Requirements

- MicroPython firmware for Raspberry Pi Pico W
- Custom PicoW-PumPi software (included in this repository)

## Setup Instructions

1. Flash the Raspberry Pi Pico W with the specified MicroPython firmware.
2. Clone this repository to your local machine.
3. Copy `config.json.template` to `config.json` and update with your specific settings:

   ```powershell
   cp config.json.template config.json
   ```

4. Edit `config.json` with your Wi-Fi credentials, MQTT broker details, and other configuration options.
5. Upload all project files to your Pico W.

## Configuration

The `config.json` file is the central configuration point for PicoW-PumPi. Key configuration sections include:

- Network settings (Wi-Fi, MQTT)
- Pump and valve control parameters
- Moisture thresholds for watering
- System update intervals

Refer to `config.json.template` for a complete list of configurable options.

## Usage

Once powered on and configured, PicoW-PumPi will:

1. Establish network connections (Wi-Fi, MQTT)
2. Initialize all pumps, valves, and switches
3. Begin listening for soil moisture data via MQTT
4. Automatically control watering based on received moisture data and configured thresholds
5. Allow manual control through physical switches

### User Interaction

- Main Pump Switch: Manual control of the main water pump
- Valve Switches (1-4): Manual control of individual solenoid valves
- MQTT Control: Remote control and monitoring via MQTT messages

## Troubleshooting

- Check `config.json` for correct network and control settings
- Ensure all hardware connections are secure
- Verify MQTT server accessibility
- Check water tank level and pump functionality regularly

## Contributing

Contributions to PicoW-PumPi are welcome! Please fork the repository and submit a pull request with your improvements.

## License

This project is open-source and available under the MIT License. See the LICENSE file for full details.

## Acknowledgments

- The MicroPython community for their excellent work
- MQTT community for robust messaging solutions
- Contributors to the original PicoW-Growmat project
