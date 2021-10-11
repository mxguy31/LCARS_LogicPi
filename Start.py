import signal
from app.logicpi import LogicPi

PLC = LogicPi()
signal.signal(signal.SIGTERM, PLC.safe_shutdown)
PLC.main()
