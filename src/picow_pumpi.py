import sys
import uasyncio
import machine
import gc
import micropython
import utime

from managers.config_manager import ConfigManager
from managers.wifi_manager import WiFiManager
from managers.mqtt_manager import MQTTManager
from managers.data_manager import DataManager
from managers.system_manager import SystemManager
from managers.log_manager import LogManager
from managers.influx_data_manager import InfluxDataManager

class PicoWPumPi:
    def __init__(self):
        micropython.alloc_emergency_exception_buf(100)
        
        self.log_mgr = LogManager()
        self.config_mgr = ConfigManager(self.log_mgr)
        self.system_mgr = SystemManager(self.config_mgr, self.log_mgr, None)
        self.data_mgr = DataManager(self.config_mgr, self.log_mgr, self.system_mgr)
        self.system_mgr.data_mgr = self.data_mgr
        self.wifi_mgr = WiFiManager(self.config_mgr, self.log_mgr)
        self.mqtt_mgr = MQTTManager(self.config_mgr, self.log_mgr)
        self.influx_data_manager = InfluxDataManager(self.config_mgr, self.log_mgr)

        self._setup_managers()
        self._initialize_state()

    def _setup_managers(self):
        self.wifi_mgr.set_system_manager(self.system_mgr)
        self.mqtt_mgr.set_system_manager(self.system_mgr)

    def _initialize_state(self):
        self.current_status = "running"
        self.last_mqtt_publish = 0
        self.last_moisture_check = 0
        self.external_watering_button_pressed = False

    async def run(self):
        await self.startup()
        await self.main_loop()

    async def startup(self):
        self.log_mgr.enable_buffering()
        self.log_mgr.log(f"Starting {self.config_mgr.MQTT_CLIENT_NAME} startup sequence...")

        await self._initialize_connections()
        await self._setup_components()
        await self._start_tasks()

        self.log_mgr.log("Startup sequence completed")

    async def _initialize_connections(self):
        self.log_mgr.log("Initializing connections...")
        try:
            await uasyncio.wait_for(self.wifi_mgr.connect(), 30)
        except uasyncio.TimeoutError:
            self.log_mgr.log("WiFi connection timed out")

        if self.system_mgr.sync_time():
            self.log_mgr.log("Time synchronized successfully")
        else:
            self.log_mgr.log("Failed to synchronize time")

    async def _setup_components(self):
        pass
    
    async def _start_tasks(self):
        uasyncio.create_task(self.mqtt_mgr.run())
        uasyncio.create_task(self.system_mgr.run())

        try:
            water_tank_level, last_watered = await uasyncio.wait_for(self.influx_data_manager.query_task(), 10)
            self.log_mgr.log(f"InfluxDb query Successful")
        except uasyncio.TimeoutError:
            self.log_mgr.log("InfluxDB query timed out")

    async def main_loop(self):
        while True:
            try:
                gc.collect()
                self.system_mgr.update_system_data()
                await self.handle_mqtt_publishing()
                await uasyncio.sleep(1)

            except Exception as e:
                self.log_mgr.log(f"Error in main loop: {e}")
                self.system_mgr.print_system_data()
                await uasyncio.sleep(5)


    async def handle_mqtt_publishing(self):
        current_time = utime.time()
        
        if current_time - self.last_mqtt_publish >= self.config_mgr.MQTT_UPDATE_INTERVAL:
            if not self.mqtt_mgr.is_connected:
                self.log_mgr.log("MQTT not connected, attempting to connect...")
                await self.mqtt_mgr.connect()
            
            if self.mqtt_mgr.is_connected:
                try:
                    prepared_mqtt_data = self.data_mgr.prepare_mqtt_data_for_publishing(
                        self.system_mgr.get_system_data(),
                        self.system_mgr.get_current_config_data()
                    )
                    publish_result = await self.mqtt_mgr.publish_data(prepared_mqtt_data)
                    if publish_result:
                        self.last_mqtt_publish = current_time
                except Exception as e:
                    self.log_mgr.log(f"MQTT publishing error: {e}")
            else:
                self.log_mgr.log("MQTT connection failed, skipping publish")