#
## Copyright (c) 2018, Bradley A. Minch
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##     1. Redistributions of source code must retain the above copyright
##        notice, this list of conditions and the following disclaimer.
##     2. Redistributions in binary form must reproduce the above copyright
##        notice, this list of conditions and the following disclaimer in the
##        documentation and/or other materials provided with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
## ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
## LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.
#

import Tkinter as tk
import paddletest
import time
import csv
import threading

class paddletestgui:

    def __init__(self):
        self.last_prog_time = 0;
        self.prog_time = 0;
        self.total_prog_time = 0L;
        self.dev = paddletest.paddlemodel()

        if self.dev.dev >= 0:
            self.update_job = None
            self.root = tk.Tk()
            self.root.title('USB Test GUI')
            self.root.protocol('WM_DELETE_WINDOW', self.shut_down)
            fm = tk.Frame(self.root)
            tk.Button(fm, text = 'LED1', command = self.dev.toggle_led1).pack(side = tk.LEFT)
            tk.Button(fm, text = 'LED2', command = self.dev.toggle_led2).pack(side = tk.LEFT)
            tk.Button(fm, text = 'LED3', command = self.dev.toggle_led3).pack(side = tk.LEFT)
            fm.pack(side = tk.TOP)
            dutyslider = tk.Scale(self.root, from_ = -50, to = 50, orient = tk.HORIZONTAL, showvalue = tk.FALSE, command = self.set_duty_callback)
            dutyslider.set(0)
            dutyslider.pack(side = tk.TOP)
            self.sw1_status = tk.Label(self.root, text = 'SW1 is currently ?')
            self.sw1_status.pack(side = tk.TOP)
            self.sw2_status = tk.Label(self.root, text = 'SW2 is currently ?')
            self.sw2_status.pack(side = tk.TOP)
            self.sw3_status = tk.Label(self.root, text = 'SW3 is currently ?')
            self.sw3_status.pack(side = tk.TOP)
            # self.a0_status = tk.Label(self.root, text = 'A0 is currently ????')
            # self.a0_status.pack(side = tk.TOP)
            self.duty_status = tk.Label(self.root, text = 'Duty cycle is currently ??%')
            self.duty_status.pack(side = tk.TOP)
            self.raw_speed = tk.Label(self.root, text= 'Speed (ticks/us): ?????')
            self.raw_speed.pack(side = tk.TOP)
            self.position = tk.Label(self.root, text='Position (ticks): ?????')
            self.position.pack(side=tk.TOP)
            self.micros_status = tk.Label(self.root, text = 'Program Time: ?????')
            self.micros_status.pack(side = tk.TOP)
            self.encoder_status = tk.Label(self.root, text = 'Encoder Angle: ?????')
            self.encoder_status.pack(side = tk.TOP)
            self.current_status = tk.Label(self.root, text = 'Current: ?????')
            self.current_status.pack(side = tk.TOP)
            self.update_status()

    def set_duty_callback(self, value):
        self.dev.set_duty(float(value))

    def update_status(self):
        self.sw1_status.configure(text = 'SW1 is currently {!s}'.format(self.dev.read_sw1()))
        self.sw2_status.configure(text = 'SW2 is currently {!s}'.format(self.dev.read_sw2()))
        self.sw3_status.configure(text = 'SW3 is currently {!s}'.format(self.dev.read_sw3()))
        # self.a0_status.configure(text = 'A0 is currently {:04d}'.format(self.dev.read_a0()))
        self.duty_status.configure(text = 'Duty cycle is currently {0:.0f}%'.format(self.dev.get_duty()))
        speed, position = self.dev.get_speed_and_position()
        self.raw_speed.configure(text='Speed: {0:.05f}'.format(speed))
        self.position.configure(text='Position: {:08d}'.format(position))
        self.dev.get_speed_and_position()
        self.micros_status.configure(text = 'Program Time: {:08d}'.format(self.dev.get_time()))
        self.encoder_status.configure(text = 'Encoder Angle: {0:.0f}'.format(self.dev.get_raw_angle()))
        self.current_status.configure(text = 'Current: {0:04d}'.format(self.dev.get_current()))
        self.update_job = self.root.after(25, self.update_status)

    def shut_down(self):
        self.root.after_cancel(self.update_job)
        self.root.destroy()
        self.dev.close()



class PIDControl:
    def __init__(self):
        self.dev = paddletest.paddlemodel()
        #self.dState = 0
        self.iState = 0
        self.iMax = 20000
        self.iMin = -20000
        self.pGain = -.005
        self.iGain = -.001
        #self.dGain = 100
        self.speed, self.position = self.dev.get_speed_and_position()
        self.target = self.position

    # def get_error(self):
    #     positions = []
    #     for i in range(0,10):
    #         position = self.dev.get_angle()
    #         positions.append(position)
    #         time.sleep(.001)
    #     position = sum(positions)/10
    #     error = self.position - position
    #     if error > 10000:
    #         error = self.position - (position+16384)
    #     elif error < -10000:
    #         error = (self.position + 16384) - position
    #     return (position, error)

    def get_error(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        error = self.target - self.position
        return (self.position, error)

    def update_pid(self):
        position, error = self.get_error()
        pTerm = self.pGain * error
        if (pTerm > 100):
            pTerm = 100
        if (pTerm < -100):
            pTerm = -100
        iState = self.iState
        iState += error
        if iState > self.iMax:
            iState = self.iMax
        elif iState < self.iMin:
            iState = self.iMin

        iTerm = self.iGain * iState
        # dTerm = self.dGain * (self.dState - position)
        # self.dState = dState
        self.iState = iState
        #drive = pTerm + iTerm + dTerm
        # drive = pTerm + iTerm
        drive = pTerm
        #duty = (drive/45.5)/1000.0 #convert to degrees, then divide by top speed of 100000 deg/.1 sec and multiply by 100 for duty cycle
        self.dev.set_duty(drive)
        print position, error, drive
        time.sleep(.01)

def update_control(pid_obj):
    while True:
        pid_obj.update_pid()

class WallControl:
    def __init__(self):
        self.dev = paddletest.paddlemodel()
        self.speed, self.position = self.dev.get_speed_and_position()
        self.target = self.position + 1000

    def get_error(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        error = self.target - self.position
        return (self.position, error)

    def update_pid(self):
        position, error = self.get_error()
        if (position > self.target):
            pTerm = 100
        else:
            pTerm = 0

        drive = pTerm

        self.dev.set_duty(drive)

        print position, error, drive
        time.sleep(.01)

class DamperControl:
    def __init__(self):
        self.dev = paddletest.paddlemodel()
        self.speed, self.position = self.dev.get_speed_and_position()

    def update_pid(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        drive = self.speed * 70

        self.dev.set_duty(drive)

        print self.position, drive
        time.sleep(.01)

class TextureControl:
    def __init__(self):
        self.dev = paddletest.paddlemodel()
        self.speed, self.position = self.dev.get_speed_and_position()
        self.bump_period = 10000

    def update_pid(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        drive = (self.position % self.bump_period) * 40 / 2500 # max 20 percent in any direction
        print (self.position % self.bump_period)
        self.dev.set_duty(drive)

        print self.position, drive
        time.sleep(.01)


class paddlecontrolgui:

    def __init__(self, control=0):
        self.dev = paddletest.paddlemodel()
        self.speed, self.position = self.dev.get_speed_and_position()
        self.bump_period = 2500
        self.control = control
        self.target = self.position + 1000
        self.iState = 0
        self.iMax = 20000
        self.iMin = -20000
        self.pGain = -.005
        self.iGain = -.001
        self.time = 0
        self.drive = 0

        if self.dev.dev >= 0:
            self.update_job = None
            self.root = tk.Tk()
            self.root.title('Paddle Test GUI')
            self.root.protocol('WM_DELETE_WINDOW', self.shut_down)
            fm = tk.Frame(self.root)
            tk.Button(fm, text = 'Damper', command = lambda: self.change_control(0)).pack(side = tk.LEFT)
            tk.Button(fm, text = 'Texture', command = lambda: self.change_control(1)).pack(side = tk.LEFT)
            tk.Button(fm, text = 'Wall', command = lambda: self.change_control(2)).pack(side = tk.LEFT)
            tk.Button(fm, text = 'Spring', command = lambda: self.change_control(3)).pack(side = tk.LEFT)
            fm.pack(side = tk.TOP)
            self.micros_status = tk.Label(self.root, text = 'Program Time: ?????')
            self.micros_status.pack(side = tk.TOP)
            self.update_status()

    def change_control(self, new):
        self.control = new
    def update_status(self):
        if self.control == 0:
            self.update_damper()
        elif self.control == 1:
            self.update_texture()
        elif self.control == 2:
            self.update_wall()
        elif self.control == 3:
            self.update_spring()
        self.time =self.dev.get_time()
        self.micros_status.configure(text = 'Program Time: {:08d}'.format(self.time))
        self.update_job = self.root.after(25, self.update_status)

    def update_texture(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        drive = (self.position % self.bump_period) * 40 / 2500 # max 20 percent in any direction
        print (self.position % self.bump_period)
        self.drive = drive
        self.dev.set_duty(drive)

        print self.position, drive
        time.sleep(.01)

    def update_damper(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        drive = self.speed * 70
        self.drive = drive
        self.dev.set_duty(drive)

        print self.position, drive
        time.sleep(.01)

    def update_wall(self):
        position, error = self.get_error()
        if (position > self.target):
            pTerm = 100
        else:
            pTerm = 0
        drive = pTerm
        self.drive = drive
        self.dev.set_duty(drive)
        time.sleep(.01)

    def update_spring(self):
        position, error = self.get_error()
        pTerm = self.pGain * error
        if (pTerm > 100):
            pTerm = 100
        if (pTerm < -100):
            pTerm = -100
        iState = self.iState
        iState += error
        if iState > self.iMax:
            iState = self.iMax
        elif iState < self.iMin:
            iState = self.iMin

        iTerm = self.iGain * iState
        # dTerm = self.dGain * (self.dState - position)
        # self.dState = dState
        self.iState = iState
        #drive = pTerm + iTerm + dTerm
        # drive = pTerm + iTerm
        drive = pTerm
        #duty = (drive/45.5)/1000.0 #convert to degrees, then divide by top speed of 100000 deg/.1 sec and multiply by 100 for duty cycle
        self.drive = drive
        self.dev.set_duty(drive)
        print position, error, drive
        time.sleep(.01)

    def get_error(self):
        self.speed, self.position = self.dev.get_speed_and_position()
        error = self.target - self.position
        return (self.position, error)

    def set_duty_callback(self, value):
        self.dev.set_duty(float(value))

    def shut_down(self):
        self.root.after_cancel(self.update_job)
        self.root.destroy()
        self.dev.close()
def run_test():
    with open('control_log_damper.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        dev = paddlecontrolgui(0)

        t = threading.Thread(target=log_data, args=(dev,writer,)) # Set up daemon thread to log data
        t.setDaemon(True)
        t.start()                                                 # Start logging data

        dev.root.mainloop()

def log_data(dev, writer): # Daemon function that will log data
    while True:
        writer.writerow([dev.time, dev.speed, dev.drive])
        time.sleep(.01)

if __name__=='__main__':
    # run_test();

    gui = paddlecontrolgui()
    gui.root.mainloop()

    # control_thread = threading.Thread(target=update_control, args=(control,)) # Set up daemon thread to run controller
    # control_thread.setDaemon(True)
    # control_thread.start()

    time.sleep(2)

    # control.target = control.position + 900 # Step functio
    while True:
        pass
