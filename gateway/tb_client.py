import logging
import time
from tb_client.tb_gateway_mqtt import TBGatewayMqttClient
from tb_utility.tb_utility import TBUtility

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TBClient:
    def __init__(self, config):
        self.__config = config
        self.__host = config["host"]
        self.__port = config.get("port", 1883)
        credentials = config["security"]
        self.__tls = False
        self.__ca_cert = None
        self.__private_key = None
        self.__cert = None
        self.__token = None
        if credentials.get("accessToken") is not None:
            self.__token = str(credentials["accessToken"])
        else:
            self.__tls = True
            self.__ca_cert = credentials.get("caCert")
            self.__private_key = credentials.get("privateKey")
            self.__cert = credentials.get("cert")
        self.client = TBGatewayMqttClient(self.__host, self.__port, self.__token, self)
        # Adding callbacks
        self.client._client._on_connect = self._on_connect
        # self._client._client._on_message = self._on_message
        self.client._client._on_disconnect = self._on_disconnect

    def is_connected(self):
        return self.client.is_connected

    def _on_connect(self, client, userdata, flags, rc, *extra_params):
        log.debug('Gateway connected to ThingsBoard')
        self.client._on_connect(client, userdata, flags, rc, *extra_params)

    def _on_disconnect(self, client, userdata, rc):
        log.info('Gateway was disconnected trying to reconnect')

    def disconnect(self):
        self.client.disconnect()

    def connect(self):
        keep_alive = self.__config.get("keep_alive", 60)

        while not self.client.is_connected():
            try:
                self.client.connect(tls=self.__tls,
                                    ca_certs=self.__ca_cert,
                                    cert_file=self.__cert,
                                    key_file=self.__private_key,
                                    keepalive=keep_alive)
            except Exception as e:
                log.error(e)
            log.debug("connecting to ThingsBoard...")
            time.sleep(1)