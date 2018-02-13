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
        self.SET_DUTY_VAL_FORWARD = 7
        self.GET_DUTY_VAL_FORWARD = 8
        self.GET_DUTY_MAX_FORWARD = 9
        self.SET_DUTY_VAL_REVERSE = 10
        self.GET_DUTY_VAL_REVERSE = 11
        self.GET_DUTY_MAX_REVERSE = 12
        self.ENC_READ_REG = 13

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

    def set_duty_val_forward(self, val):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_VAL_FORWARD, val)
        except usb.core.USBError:
            print "Could not send SET_DUTY_VAL vendor request."

    def set_duty_val_reverse(self, val):
        try:
            self.dev.ctrl_transfer(0x40, self.SET_DUTY_VAL_REVERSE, val)
        except usb.core.USBError:
            print "Could not send SET_DUTY_VAL vendor request."

    def get_duty_val_reverse(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_VAL_REVERSE, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_VAL vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])
    def get_duty_val_forward(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_VAL_FORWARD, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_VAL vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])

    def get_duty_max_forward(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MAX_FORWARD, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_MAX vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])
    def get_duty_max_reverse(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.GET_DUTY_MAX_REVERSE, 0, 0, 2)
        except usb.core.USBError:
            print "Could not send GET_DUTY_MAX vendor request."
        else:
            return int(ret[0]) + 256 * int(ret[1])

    def set_duty(self, duty_cycle):
        if duty_cycle >= 0:
            val = int(round(duty_cycle * self.get_duty_max_forward() / 100.))
            self.set_duty_val_forward(val)
            self.set_duty_val_reverse(0)
        elif duty_cycle < 0:
            val = int(round(-duty_cycle * self.get_duty_max_reverse() / 100.))
            self.set_duty_val_reverse(val)
            self.set_duty_val_forward(0)


    def get_duty(self):
        forward_duty = 100. * self.get_duty_val_forward() / self.get_duty_max_forward()
        if forward_duty > 0:
            return forward_duty
        elif type(self.get_duty_val_reverse) is int:
            return -100. * self.get_duty_val_reverse() / self.get_duty_max_reverse()
        else:
            return 0.

    # def enc_readReg(self, address):
    #     try:
    #         ret = self.dev.ctrl_transfer(0xC0, self.ENC_READ_REG, address, 0, 2)
    #     except usb.core.USBError:
    #         print "Could not send ENC_READ_REG vendor request."
    #     else:
    #         return ret

    def get_angle(self):
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.ENC_READ_REG, 0x3FFF, 0, 2)
        except usb.core.USBError:
            print "Could not send ENC_READ_REG vendor request."
        else:
            sensed = (int(ret[0]) + 256 * int(ret[1])) & 0x3FFF
            return sensed/16400.0 *360.0
