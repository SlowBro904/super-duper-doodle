#!/usr/bin/env python3.5
import test_suite
from time import sleep
import lib.leds as leds

good = test_suite.good

leds = leds.LEDs()

leds.LED('good', default = True)
assert leds.good.value == True, "Cannot set the good LED"
assert leds.warn.value == False, "Cannot set the warn LED"
assert leds.err.value == False, "Cannot set the err LED"
good("Set the good LED")

leds.LED()
assert leds.good.value == True, "Cannot set the good LED"
assert leds.warn.value == False, "Cannot set the warn LED"
assert leds.err.value == False, "Cannot set the err LED"
good("Back to the default")

leds.LED('warn')
assert leds.good.value == False, "Cannot set the good LED"
assert leds.warn.value == True, "Cannot set the warn LED"
assert leds.err.value == False, "Cannot set the err LED"
good("Set the warn LED")

leds.LED()
leds.LED('err')
assert leds.good.value == False, "Cannot set the good LED"
assert leds.warn.value == False, "Cannot set the warn LED"
assert leds.err.value == True, "Cannot set the err LED"
good("Set the err LED")

leds.LED()
assert leds.good.value == True, "Cannot set the good LED"
assert leds.warn.value == False, "Cannot set the warn LED"
assert leds.err.value == False, "Cannot set the err LED"
good("Back to the default")

leds.LED(default = True)
assert leds.good.value == True, "Cannot set the good LED"
assert leds.warn.value == False, "Cannot set the warn LED"
assert leds.err.value == False, "Cannot set the err LED"
good("All off")