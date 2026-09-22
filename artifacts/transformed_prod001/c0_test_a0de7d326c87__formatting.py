import requests
from functools import partial


class IoTDevice:
    def __init__(self, uri, protocol="http"):
        self.uri = uri
        self.protocol = protocol

    def send_http_request(self, endpoint, data=None):
        if self.protocol == "http":
            response = requests.get(f"{self.uri}/{endpoint}", json=data)
            return response.json()
        else:
            raise ValueError("Unsupported protocol for HTTP request")

    def send_coap_request(self, endpoint, data=None):
        # Placeholder for CoAP request logic; assumes a similar method exists
        print(f"Sending CoAP request to {self.uri}/{endpoint} with data: {data}")

    def connect(self, endpoint, data=None):
        if self.protocol == "http":
            return self.send_http_request(endpoint, data)
        elif self.protocol == "coap":
            return self.send_coap_request(endpoint, data)
        else:
            raise ValueError("Unsupported protocol")


# Example usage
if __name__ == "__main__":
    device = IoTDevice("http://example-iot-device", protocol="http")
    data = device.connect("sensor/data", data={"value": 42})
    print(data)

    coap_device = IoTDevice("coap://example-iot-coap-device", protocol="coap")
    coap_device.connect("sensor/status", data={"status": "active"})
