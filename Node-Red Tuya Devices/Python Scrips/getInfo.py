import tinytuya

device = tinytuya.Device('DEVICE_ID', 'IP_ADDRESS', 'LOCAL_KEY')
device.set_version(TUYA_VERSION)
status = device.status()
dps = device.detect_available_dps() 
print('Device status: %r\n' % data)
print('DPS Availible: %r\n' % data)