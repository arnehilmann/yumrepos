import logging
import logging.handlers

log = logging.getLogger()

log.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address='/dev/log')
# handler = logging.handlers.SysLogHandler()

formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)

log.addHandler(handler)
log.info("syslog subsystem started")
