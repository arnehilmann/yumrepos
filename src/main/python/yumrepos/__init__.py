import logging
import logging.handlers

log = logging.getLogger()

log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()

formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)

log.addHandler(handler)
