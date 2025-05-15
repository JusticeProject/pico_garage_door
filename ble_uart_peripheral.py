# This example demonstrates a peripheral implementing the Nordic UART Service (NUS).

# This example demonstrates the low-level bluetooth module. For most
# applications, we recommend using the higher-level aioble library which takes
# care of all IRQ handling and connection management. See
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

import bluetooth
from ble_advertising import advertising_payload

from micropython import const

###############################################################################

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

###############################################################################

class BLE_UART:
    def __init__(self, name, rxbuf=100):
        self.__ble = bluetooth.BLE()
        self.__ble.active(True)
        self.__ble.irq(self.__irq)
        ((self.__tx_handle, self.__rx_handle),) = self.__ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self.__ble.gatts_set_buffer(self.__rx_handle, rxbuf, True)
        self.__connections = set()
        self.__rx_buffer = bytearray()
        self.__handler = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self.__payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self.__advertise()

    def set_rx_callback(self, handler):
        self.__handler = handler

    def __irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.__connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self.__connections:
                self.__connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self.__advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self.__connections and value_handle == self.__rx_handle:
                self.__rx_buffer += self.__ble.gatts_read(self.__rx_handle)
                if self.__handler:
                    self.__handler()

    def read(self, sz=None):
        if not sz:
            sz = len(self.__rx_buffer)
        result = self.__rx_buffer[0:sz]
        self.__rx_buffer = self.__rx_buffer[sz:]
        return result

    def write(self, data):
        for conn_handle in self.__connections:
            self.__ble.gatts_notify(conn_handle, self.__tx_handle, data) # type: ignore

    def close(self):
        for conn_handle in self.__connections:
            self.__ble.gap_disconnect(conn_handle)
        self.__connections.clear()

    def __advertise(self, interval_us=500000):
        self.__ble.gap_advertise(interval_us, adv_data=self.__payload) # type: ignore

