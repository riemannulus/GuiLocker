import os
import sys
import shlex
import logging
from time import sleep
from subprocess import call, PIPE, Popen

from tkinter import *

#  class GuiApp(tk.Tk):
#  self.__password = ""
#
#  def __init__(self):
#      tk.Tk.__init__(self)
#      self.geometry('300x250')
#      self.label = tk.Label(self, text="Input bitlocker password")
#      self.entry = tk.Entry(self)
#      self.button = tk.Button(self, text="Unlock", command=self.on_button)
#      self.label.pack(side=tk.LEFT)
#      self.entry.pack(side=tk.LEFT)
#      self.button.pack(side=tk.LEFT)
#
#  def on_button(self):
#      self.__password = self.entry.get()
#  self.destroy()

class GuiLocker():
    bitlocker_path = "/media/bitlocker"

    def __init__(self):
        if os.getuid() != 0:
            raise Exception("Permission denied. require root.")
        logging.basicConfig(filename='guilocker.log', level=logging.DEBUG)
        logging.info('Program Started')

    def __is_bitlocker(self, disk):
        device_path = self.__get_device_path(disk)
        command = f"dislocker -r -V {device_path}"

        p = Popen(shlex.split(command), stdout=PIPE)
        stdout = p.stdout.read().decode("utf-8")

        print(disk)
        print(stdout)
        print("="*15)

        if "Cannot parse volume header" in stdout:
            return False
        elif "None of the provided decryption mean" in stdout:
            return True
        elif "No such file or directory" in stdout:
            return False
        else:
            raise Exception(f"Unexpected exception.: {stdout}")

    def __get_disks(self):
        with open("/proc/partitions", "r") as f:
            devices = []
            for line in f.readlines()[2:]:
                elements = list(map(lambda x: x.strip(), line.split()))
                if 'loop' in elements[3]:
                    continue
                devices.append(elements[3])

            return devices

    def __get_device_path(self, device):
        return f"/dev/{device}"

    def __get_device_model_name(self, device):
        device_path = self.__get_device_path(device)
        logging.debug('__get_device_model: ' + device_path)
        command = ''
        if len(device) == 3:
            command = f"fdisk -l {device_path}"
        else:
            command = f"fdisk -l {device_path}"[:-1]

        p = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
        stdout = p.stdout.read().decode("utf-8")
        stderr = p.stderr.read().decode("utf-8")

        if len(stdout) == 0:
            raise Exception

        disk_model = stdout.split("\n")[1].split()[2]
        return disk_model

    def __get_mount_path(self, device):
        device_path = self.__get_device_path(device)
        disk_model = self.__get_device_model_name(device)
        path = "/media/" + disk_model
        return path

    def __is_mounted(self, device):
        device_model = self.__get_device_model_name(device)
        logging.debug('__is_mounted: ' + device_model)
        with open('/proc/mounts', 'r') as f:
            for line in f.readlines():
                if device in line:
                    return True
                elif device_model in line:
                    return True

        return False

    def mount(self, device, password):
        device_path = self.__get_device_path(device)
        mount_path = self.__get_mount_path(device)
        dislocker_cmd = f'dislocker -r -V {device_path} -u"{password}" -- {self.bitlocker_path}'
        mkdir_cmd = f"mkdir -p {mount_path} {self.bitlocker_path}"
        mount_cmd = f"mount -r -o loop {self.bitlocker_path}/dislocker-file {mount_path}"

        dis_proc = Popen(shlex.split(dislocker_cmd))
        mkdir_proc = Popen(shlex.split(mkdir_cmd))
        sleep(1)
        mount_proc = Popen(shlex.split(mount_cmd))
        sleep(1)

        if self.__is_mounted(device):
            logging.debug('Successful mounted')
            return True
        else:
            logging.debug('Mount failed')
            return False

    def umount(self, device):
        mount_path = self.__get_mount_path(device)
        device_path = self.__get_device_path(device)
        umount_cmd = f"umount {mount_path} {self.bitlocker_path}"
        rm_cmd = f"rm -rf {mount_path} {self.bitlocker_path}"

        p = Popen(shlex.split(umount_cmd))
        sleep(1)
        p2 = Popen(shlex.split(rm_cmd))

        if self.__is_mounted(device):
            logging.debug('Unmount failed')
            return True
        else:
            logging.debug('Successful unmounted')
            return False

    def get_password_gui(self):
        self._password = ''

        root = Tk()
        root.title("GuiLocker GUI")
        root.geometry('400x200')
        pwentry = Entry(root, show = '*')

        def on_unlock_click():
            self._password = pwentry.get()
            root.destroy()

        Label(root, text = "Enter the device password: ").pack(side='top')
        pwentry.pack(side='left')
        Button(root, command=on_unlock_click, text = 'Unlock').pack(side='left')

        root.mainloop()
        return self._password

    def run(self):
        logging.debug('Start Run')
        while True:
            devices = self.__get_disks()
            unmounted_devices = [d for d in devices if not self.__is_mounted(d)]

            logging.debug(''.join(unmounted_devices))

            if len(devices) == 0:
                sleep(1)
                continue

            for d in devices:
                if self.__is_bitlocker(d) and not self.__is_mounted(d):
                    password = self.get_password_gui()
                    self.mount(d, password)

            sleep(1)

if __name__ == "__main__":
    g = GuiLocker()
    g.run()
