import os
import shlex
import logging
from time import sleep
from subprocess import PIPE, Popen


class Core():
    bitlocker_path = "/media/bitlocker"

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

    def get_mounted_device(self):
        devices = self.__get_disks()

        for d in devices:
            if self.__is_bitlocker(d) and self.__is_mounted(d):
                return d
        return False

    def mount(self, device, password):
        device_path = self.__get_device_path(device)
        mount_path = self.__get_mount_path(device)
        dislocker_cmd = f'dislocker -r -V {device_path} -u"{password}" -- {self.bitlocker_path}'
        mkdir_cmd = f"mkdir -p {mount_path} {self.bitlocker_path}"
        mount_cmd = f"mount -r -o loop {self.bitlocker_path}/dislocker-file {mount_path}"

        Popen(shlex.split(dislocker_cmd))
        Popen(shlex.split(mkdir_cmd))
        sleep(1)
        Popen(shlex.split(mount_cmd))
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
        bitlocker_umount_cmd = f"umount {mount_path} {self.bitlocker_path}"
        device_umount_cmd = f"umount {mount_path} {device_path}"
        rm_cmd = f"rm -rf {mount_path} {self.bitlocker_path}"

        Popen(shlex.split(device_umount_cmd))
        sleep(0.5)
        Popen(shlex.split(bitlocker_umount_cmd))
        sleep(0.5)
        Popen(shlex.split(rm_cmd))

        if self.__is_mounted(device):
            logging.debug('Unmount failed')
            return True
        else:
            logging.debug('Successful unmounted')
            return False

