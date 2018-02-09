import usb.core
import time

class paddlemodel:

    def __init__(self):
        self.TOGGLE_LED1 = 0
        self.TOGGLE_LED2 = 1
        self.TOGGLE_LED3 = 2
        self.READ_SW1 = 3
        self.READ_SW2 = 4
        self.READ_SW3 = 5
        self.READ_A0 = 6
        self.SET_DUTY_VAL = 7
        self.GET_DUTY_VAL = 8
        self.GET_DUTY_MAX = 9
        self.ENC_READ_REG = 10

        self.dev = usb.core.find(idVendor = 0x6666, idProduct = 0x0003)
        if self.dev is None:
            raise ValueError('no USB device found matching idVendor = 0x6666 and idProduct = 0x0003')
        self.dev.set_configuration()

# AS5048A Register Map
        self.ENC_NOP = 0x0000
        self.ENC_CLEAR_ERROR_FLAG = 0x0001
        self.ENC_PROGRAMMING_CTRL = 0x0003
        self.ENC_OTP_ZERO_POS_HI = 0x0016
        self.ENC_OTP_ZERO_POS_LO = 0x0017
        self.ENC_DIAG_AND_AUTO_GAIN_CTRL = 0x3FFD
        self.ENC_MAGNITUDE = 0x3FFE
        self.ENC_ANGLE_AFTER_ZERO_POS_ADDER = 0x3FFF

    def close(self):
        self.dev = None

    def toggle_led1(self):
        try:
            self.dev.ctrl_transfer(0x40, self.TOGGLE_LED1)
        except usb.core.USBError:
            print "Could not send TOGGLE_LED1 vendor request."

    def toggle_led2(self):
        try:
            self.dev.ctrl_transfer(0x40, self.TOGGLE_LED2)
        except usb.core.USBError:
            print "Could not send TOGGLE_LED2 vendor request."

    def toggle_led3(self):
        try:
            self.dev.ctrl_transfer(0x40, self.TOGGLE_LED3)
        except usb.core.USBError:
            print "Could not send TOGGLE_LED3 vendor request."

    def read_sw1(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.READ_SW1, 0, 0, 1)
        except usb.core.USBError:
            print "Could not send READ_SW1 vendor request."
        else:
            return int(ret[0])

    def read_sw2(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.READ_SW2, 0, 0, 1)
        except usb.core.USBError:
            print "Could not send READ_SW2 vendor request."
        else:
            return int(ret[0])

    def read_sw3(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.READ_SW3, 0, 0, 1)
        except usb.core.USBError:
            print "Could not send READ_SW3 vendor request."
        else:
            return int(ret[0])
    def read_a0(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.READ_A0, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send READ_A0 vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])

    def set_duty_val(self, val):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_VAL, val)
        except usb.core.USBError:
            print "Could not send SET_DUTY_VAL vendor request."

    def get_duty_val(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_VAL, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_VAL vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])

    def get_duty_max(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MAX, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_MAX vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])

    def set_duty(self, duty_cycle):
        val = int(round(duty_cycle * self.get_duty_max() / 100.))
        self.set_duty_val(val)

    def get_duty(self):
        return 100. * self.get_duty_val() / self.get_duty_max()

    def enc_readReg(self, address):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.ENC_READ_REG, address, 0, 2)
        except usb.core.USBError:
            print "Could not send ENC_READ_REG vendor request."
        else:
            return ret

    def get_angle(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.ENC_READ_REG, 0x3FFF, 0, 2)
        except usb.core.USBError:
            print "Could not send ENC_READ_REG vendor request."
        else:
            return (int(ret[0]) + 256 * int(ret[1])) & 0x3FFF
