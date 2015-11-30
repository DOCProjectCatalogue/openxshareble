
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART as OriginalUART
# from ble import uart
from ble.uart import UART
import time
import logging
log = logging.getLogger(__name__)

class App (object):
  def __init__ (self, **kwds):
    self.disconnect_on_after = kwds.get('disconnect_on_after', False)
    pass
  def setup_ble (self, clear_cached_data=True, disconnect_devices=True, scan_devices=True, connect=True):
    self.device = None
    self.ble = Adafruit_BluefruitLE.get_provider()
    # Initialize the BLE system.  MUST be called before other BLE calls!
    self.ble.initialize()
    pass
  def setup_dexcom (self):
    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        # print device._device.GattServices
        log.info('Discovering services...')
        UART.discover(self.device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        self.uart = UART(device)

        self.dexcom = Device(uart)
    except:
        # Make sure device is disconnected on exit.
        if self.disconnect_on_after:
          self.device.disconnect()
  def prolog (self, clear_cached_data=True, disconnect_devices=True, scan_devices=True):
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    if clear_cached_data:
      self.ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    self.adapter = ble.get_default_adapter()
    self.adapter.power_on()
    log.info('Using adapter: {0}'.format(self.adapter.name))

    if disconnect_devices:
      # Disconnect any currently connected UART devices.  Good for cleaning up and
      # starting from a fresh state.
      log.info('Disconnecting any connected UART devices...')
      UART.disconnect_devices()

    if scan_devices:
      # Scan for UART devices.
      log.info('Searching for UART device...')
      try:
          self.adapter.start_scan()
          # Search for the first UART device found (will time out after 60 seconds
          # but you can specify an optional timeout_sec parameter to change it).
          self.device = UART.find_device()
          if self.device is None:
              raise RuntimeError('Failed to find UART device!')
      finally:
          # Make sure scanning is stopped before exiting.
          self.adapter.stop_scan()

    if connect and not self.device.is_connected:
      log.info('Connecting to device...')
      self.device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                        # to change the timeout.
    log.info(self.device.name)
    # device._device.Pair( )
    log.info(self.ble._print_tree( ))
    for service in self.device.list_services( ):
      log.info(service, service.uuid)
    log.info("ADVERTISED")
    log.info(self.device.advertised)

    pass
  def enumerate_dexcoms (self, timeout_secs=10):
    self.adapter.start_scan()
    # Use atexit.register to call the adapter stop_scan function before quiting.
    # This is good practice for calling cleanup code in this main function as
    # a try/finally block might not be called since this is a background thread.
    atexit.register(self.adapter.stop_scan)
    print('Searching for UART devices...')
    # print('Press Ctrl-C to quit (will take ~30 seconds on OSX).')
    # Enter a loop and print out whenever a new UART device is found.
    start = time.time( )
    now = time.time( )
    known_uarts = set()
    while (now - start) < timeout_secs:
        # Call UART.find_devices to get a list of any UART devices that
        # have been found.  This call will quickly return results and does
        # not wait for devices to appear.
        found = set(UART.find_devices())
        # Check for new devices that haven't been seen yet and print out
        # their name and ID (MAC address on Linux, GUID on OSX).
        new = found - known_uarts
        for device in new:
            log.info('Found UART: {0} [{1}]'.format(device.name, device.id))
        known_uarts.update(new)
        # Sleep for a second and see if new devices have appeared.
        time.sleep(1.0)
        now = time.time( )
    return known_uarts

  def epilog (self):
    # Make sure device is disconnected on exit.
    if self.disconnect_on_after:
      self.device.disconnect()
    pass
  def set_handler (self, handler):
    self.handler = handler
  def run (self):
    self.ble.run_mainloop_with(self.main)
    pass
  def main (self):
    ""
