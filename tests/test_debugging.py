import test_suite
import .sys.debugging

good = test_suite.good
debug = debugging.printmsg

check = "printmsg()"
assert debug("Test") == print("[DEBUG] Test"), check
good(check)