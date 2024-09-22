import math
import utime
import ntptime
import machine

class DataManager:
    def __init__(self, config, log_mgr, system_mgr):
        self.config = config
        self.log_manager = log_mgr
        self.system_mgr = system_mgr

    
    def adjust_cpu_frequency(self, cpu_frequency):
        return cpu_frequency / 1000000


    def prepare_mqtt_data_for_publishing(self, system_data, current_config_data):
        try:
            mqtt_data = system_data
            data = {
                "system": mqtt_data["system"],
                "adc": mqtt_data["adc"],
                "current_config": current_config_data
            }
            return data
        except Exception as e:
            print(f"Error in prepare_mqtt_sensor_data_for_publishing: {e}")
            return None
