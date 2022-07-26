#!/usr/bin/env python

import sys
import gatt

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
                characteristic.enable_notifications();

    def getValue(self, byteVal, init, d):
        return ((byteVal[init]<<16) + (byteVal[init+1]<<8) + byteVal[init+2]) / d

    def characteristic_value_updated(self, characteristic, value):
        if len(value) == 20 and value[0] == 0xFF and value[2] == 0x01:
            self.valueData = value
        elif len(value) == 16:
            byteVal = self.valueData + value
            checksum = 0
            for b in byteVal[2:34]:
                checksum = checksum + b;

            if ((checksum & 0xFF) ^ 0x44) != byteVal[35]:
               print("checksum failed")
               return
            print("voltage: ", self.getValue(byteVal, 4, 100))
            print("current: ", self.getValue(byteVal, 7, 100))
            print("power: ", self.getValue(byteVal, 10, 1))

if __name__ == '__main__':

    device = AnyDevice(mac_address=sys.argv[1], manager=manager)
    device.connect()

    manager.run()
