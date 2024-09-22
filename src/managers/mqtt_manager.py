import json
import uasyncio
from umqtt_simple import MQTTClient
import utime

class MQTTManager:
    def __init__(self, config, log_mgr):
        self.config = config
        self.log_mgr = log_mgr
        self.client = None
        self.is_connected = False
        self.last_publish_time = 0
        self.system_manager = None


    def set_system_manager(self, system_manager):
        self.system_manager = system_manager

    async def publish_data(self, data):
        if not self.is_connected:
            self.log_mgr.log("MQTT not connected. Attempting to connect...")
            await self.reconnect()
        
        if not self.is_connected:
            self.log_mgr.log("MQTT connection failed. Cannot publish data.")
            return False

        try:
            for topic, subtopics in self.config.MQTT_TOPICS.items():
                if topic in data:
                    for subtopic in subtopics:
                        if subtopic in data[topic]:
                            full_topic = f"{self.config.MQTT_CLIENT_NAME}/{topic}/{subtopic}"
                            message = str(data[topic][subtopic])
                            try:
                                result = self.client.publish(full_topic.encode(), message.encode())
                            except Exception as e:
                                if self.system_manager:
                                    self.system_manager.add_error("mqtt_publish")
                                self.log_mgr.log(f"Exception while publishing to {full_topic}: {e}")
                        else:
                            self.log_mgr.log(f"Subtopic {subtopic} not found in data for topic {topic}")
                else:
                    self.log_mgr.log(f"Topic {topic} not found in data")
            
            self.last_publish_time = utime.time()
            self.log_mgr.log("MQTT data published successful")
            return True
        except Exception as e:
            self.log_mgr.log(f"Exception in publish_data: {e}")
            if self.system_manager:
                self.system_manager.add_error("mqtt_publish")
            self.is_connected = False
            return False

    async def reconnect(self):
        self.log_mgr.log("Attempting to reconnect to MQTT broker")
        try:
            self.client.disconnect()
        except:
            pass
        await self.connect()

    async def connect(self):
        if self.system_manager:
            self.system_manager.start_processing("mqtt_connect")
        self.log_mgr.log("MQTT connecting ...")
        try:
            self.client = MQTTClient(self.config.MQTT_CLIENT_NAME, self.config.MQTT_BROKER_ADDRESS, self.config.MQTT_BROKER_PORT)
            self.client.set_callback(self.on_message)
            self.client.connect()
            self.is_connected = True
            self.log_mgr.log(f"MQTT client connected as: {self.config.MQTT_CLIENT_NAME}")
            await self.subscribe_to_control_topics()
            if self.system_manager:
                self.system_manager.stop_processing("mqtt_connect")
        except Exception as e:
            self.log_mgr.log(f"Failed to connect to MQTT broker: {e}")
            self.is_connected = False
            if self.system_manager:
                self.system_manager.add_error("mqtt_connection")
                self.system_manager.stop_processing("mqtt_connect")


    async def subscribe_to_control_topics(self):
        if self.is_connected:
            try:
                self.client.subscribe(f"{self.config.MQTT_CLIENT_NAME}/control/#")
                self.client.subscribe(f"{self.config.MQTT_CLIENT_NAME}/config/#")
                self.log_mgr.log("MQTT control topics subscribed")
            except Exception as e:
                self.log_mgr.log(f"Failed to subscribe to control topics: {e}")       

    def on_message(self, topic, msg):
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8').strip()
        self.log_mgr.log(f"MQTT message received on topic {topic}: {msg}")
        
        if topic.startswith(f"{self.config.MQTT_CLIENT_NAME}/config/"):
            _, _, key = topic.split('/')
            self.handle_config_update(key, msg)
            self.config.load_from_file()
            if topic == f"{self.config.MQTT_CLIENT_NAME}/config/MOISTURE_THRESHOLD":
                # TODO: Implement pump_manager.py
                pass
            elif topic == f"{self.config.MQTT_CLIENT_NAME}/config/MOISTURE_CHECK_INTERVAL":
                # TODO: Implement pump_manager.py
                pass
                
        elif topic == f"{self.config.MQTT_CLIENT_NAME}/control/watering":
            # uasyncio.create_task(self.handle_watering_control(msg))
            # TODO: Implement pump_manager.py
            pass
        elif topic == f"{self.config.MQTT_CLIENT_NAME}/control/reset-water-tank":
            # uasyncio.create_task(self.handle_reset_water_tank(msg))
            # TODO: Implement pump_manager.py
            pass
        elif topic == f"{self.config.MQTT_CLIENT_NAME}/control/restart-system":
            # uasyncio.create_task(self.handle_system_restart(msg))
            # TODO: Implement pump_manager.py
            pass
            
    def handle_config_update(self, key, value):
        try:
            if isinstance(value, str):
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.replace('.', '').isdigit():
                    value = float(value) if '.' in value else int(value)
            
            if self.config.update_config(key, value):
                self.log_mgr.log(f"Configuration updated: {key} = {value}")
            else:
                self.log_mgr.log(f"Failed to update configuration: {key} = {value}")
        except Exception as e:
            self.log_mgr.log(f"Error updating configuration: {e}")

    # TODO: Implent MQTT control methods
    # async def handle_watering_control(self, msg):
    #     if self.m5_watering_unit is None:
    #         self.log_mgr.log("Watering unit not set. Cannot trigger watering.")
    #         return

    #     if msg.lower() == "start":
    #         self.log_mgr.log("Triggering watering via MQTT control")
    #         await self.m5_watering_unit.trigger_watering()
    #     else:
    #         self.log_mgr.log(f"Unknown control command: {msg}")
            
    # async def handle_reset_water_tank(self, msg):
    #     if self.m5_watering_unit is None:
    #         self.log_mgr.log("Watering unit not set. Cannot reset water tank.")
    #         return

    #     if msg.lower() == "reset":
    #         self.log_mgr.log("Resetting water tank level via MQTT control")
    #         self.m5_watering_unit.water_tank.reset_capacity()
    #     else:
    #         self.log_mgr.log(f"Unknown control command: {msg}")

        
    async def handle_system_restart(self, msg):
        if self.system_manager is None:
            self.log_mgr.log("System-Manager not set. Cannot restart system.")
            return
        if msg.lower() == "true":
            self.log_mgr.log("Restarting system via MQTT control")
            self.system_manager.restart_system()
        else:
            self.log_mgr.log(f"Unknown control command: {msg}")


    async def check_messages(self):
        if self.is_connected:
            try:
                self.client.check_msg()
            except Exception as e:
                self.log_mgr.log(f"Error checking messages: {e}")
                await self.reconnect()

    async def run(self):
        while True:
            if not self.is_connected:
                await self.connect()
            await self.check_messages()
            await uasyncio.sleep(0.1)  # Check messages more frequently