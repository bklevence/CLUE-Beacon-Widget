# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Auto-Cycling Eddystone Beacon for CLUE - Family Edition with Simple Rainbow
This example uses a simple rainbow effect without additional libraries.
"""

import time
from adafruit_pybadger import pybadger
import adafruit_ble
from adafruit_ble_eddystone import uid, url

radio = adafruit_ble.BLERadio()

# Reuse the BLE address as our Eddystone instance id.
eddystone_uid = uid.EddystoneUID(radio.address_bytes)

# Rainbow animation settings - adjust these to change speed
RAINBOW_SPEED = 1  # How much to increment each cycle (1-10, higher = faster)
RAINBOW_DELAY = 0.05  # Delay between updates (0.01-0.2, higher = slower)

# Rainbow color wheel function
def colorwheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# List of URLs to broadcast here with their corresponding BMP files and LED colors:
ad_url = [("", "HOME LAB", "cluebeacon.bmp", "RAINBOW"),  # Splash screen
          ("about:blank", "JELLYFIN", "jellyfin.bmp", pybadger.YELLOW),
          ("about:blank", "KAVITA", "kavita.bmp", pybadger.GREEN),
          ("about:blank", "REQUESTS", "requests.bmp", pybadger.PURPLE)
         ]

pick = 0  # use to increment url choices
rainbow_pos = 0  # position in rainbow cycle

pybadger.play_tone(1600, 0.25)

# Initial setup
if ad_url[pick][3] == "RAINBOW":
    pybadger.pixels.fill(colorwheel(rainbow_pos))
else:
    pybadger.pixels.fill(ad_url[pick][3])

pybadger.show_business_card(image_name=ad_url[pick][2])

# Set last_switch AFTER initial setup so splash screen gets full time
last_switch = time.monotonic()

while True:
    # Update rainbow animation for splash screen (moved to top for priority)
    if ad_url[pick][3] == "RAINBOW":
        rainbow_pos = (rainbow_pos + RAINBOW_SPEED) % 256  # Increment rainbow position
        pybadger.pixels.fill(colorwheel(rainbow_pos))

    pybadger.auto_dim_display(delay=3, movement_threshold=4)

    # Auto-cycle with longer time for splash screen
    if ad_url[pick][3] == "RAINBOW":
        cycle_time = 15  # Splash screen shows for 15 seconds
    else:
        cycle_time = 5   # Other pages show for 5 seconds

    if time.monotonic() - last_switch > cycle_time:
        pick = (pick + 1) % len(ad_url)
        pybadger.brightness = 1

        # Set initial color for new selection
        if ad_url[pick][3] != "RAINBOW":
            pybadger.pixels.fill(ad_url[pick][3])

        if ad_url[pick][0]:  # Has URL
            pybadger.show_business_card(image_name=ad_url[pick][2], name_string=ad_url[pick][1], name_scale=5,
                                        email_string_one="", email_string_two=ad_url[pick][0])
        else:  # Splash screen
            pybadger.show_business_card(image_name=ad_url[pick][2])
        last_switch = time.monotonic()

    # Create eddystone URL only if we have one (only during non-rainbow or less frequently)
    if ad_url[pick][0]:
        eddystone_url = url.EddystoneURL(ad_url[pick][0])

        # Both buttons show QR code
        if pybadger.button.a or pybadger.button.b:
            pybadger.play_tone(1200, 0.1)
            pybadger.brightness = 1
            pybadger.show_qr_code(data=ad_url[pick][0].encode("utf-8"))
            time.sleep(15)  # Hold QR code for 15 seconds
            time.sleep(0.1)  # Debounce
            # Restore rainbow after QR code if on splash
            if ad_url[pick][3] == "RAINBOW":
                pybadger.pixels.fill(colorwheel(rainbow_pos))

        # Only do BLE advertising occasionally to not interrupt rainbow
        if int(time.monotonic() * 2) % 4 == 0:  # Every 2 seconds instead of every loop
            # Alternate between advertising our ID and our URL.
            radio.start_advertising(eddystone_uid)
            time.sleep(0.5)
            radio.stop_advertising()

            radio.start_advertising(eddystone_url)
            time.sleep(0.5)
            radio.stop_advertising()
    else:
        # No advertising for splash screen, minimal delay for smooth rainbow
        if ad_url[pick][3] == "RAINBOW":
            time.sleep(RAINBOW_DELAY)  # Just the rainbow delay
        else:
            time.sleep(1)

    # Only add extra delay for non-rainbow pages
    if ad_url[pick][3] != "RAINBOW":
        time.sleep(RAINBOW_DELAY)
