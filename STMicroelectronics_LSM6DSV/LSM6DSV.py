import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from LSM6DSV_definitions import *
from ctypes import *

def find_matching_item(data, target_pid):
    for item in data:
        if item.get('pid') == target_pid:
            return item
    return None

class LSM6DSV:
    pid = [0x02, 0x08, 0x00, 0x70, 0x92, 0x0B]
    pid = [f"0x{num:02x}" for num in pid]
    address = None

    # Sensor configuration
    accel_mode = LSM6DSV_ACCEL_OP_MODES.HIGH_PERFORMANCE.value
    accel_odr = LSM6DSV_ACCEL_ODR.AODR_240Hz.value
    accel_fs = LSM6DSV_ACCEL_FS.FS_2g.value
    
    gyro_mode = LSM6DSV_GYRO_OP_MODES.HIGH_PERFORMANCE.value
    gyro_odr = LSM6DSV_GYRO_ODR.GODR_240Hz.value
    gyro_fs = LSM6DSV_GYRO_FS.FS_250dps.value

    # Calibration
    accel_bias = None
    gyro_bias = None

    def __init__(self, i3c):
        self.i3c = i3c

        (_, targets) = i3c.targets()

        lmi_device = find_matching_item(targets, self.pid)

        if lmi_device is None:
            print("LSM6DSV device not found in the I3C bus")
            return
        
        self.address = lmi_device["dynamic_address"]

    def __calculate_resolution(self):
        '''
        Calculate the resolutions of the sensor based on the current configuration.
        Use the respective full scale values and the number of bits (16) to calculate the resolutions.
        '''
        a_res = LSM6DSV_ACCEL_FS_VALUES[self.accel_fs] / LSM6DSV_ACCEL_RESOLUTION
        g_res = LSM6DSV_GYRO_FS_VALUES[self.gyro_fs] / LSM6DSV_GYRO_RESOLUTION

        return (a_res, g_res)
    
    def __read_data(self):
        '''
        Read the data from the sensor. The data is read in a single transaction starting from the
        gyroscope data X register. The data is then converted to signed 16-bit integers.
        '''
        # The three components of the accelerometer and gyroscope are 2-bytes length each
        READ_LEN = 12

        # Read data
        (_, raw_data) = self.i3c.read(self.address, self.i3c.TransferMode.I3C_SDR, [LSM6DSV_GYRO_DATA_X], READ_LEN)

        # Convert data to signed 16-bit integers
        imu_data = [0, 0, 0, 0, 0, 0]
        for i in range(len(imu_data)):
            imu_data[i] = c_int16((raw_data[2*i + 1] << 8) | raw_data[2*i]).value
        
        return imu_data
    
    def init_device(self):
        '''
        Initialize the sensor with the current configuration. Uses two configuration registers of
        1 byte each for both the accelerometer and the gyroscope.
        '''
        # Set accelerometer configuration
        LSM6DSV_ACCEL_CONFIG_1 = [self.accel_mode | self.accel_odr]
        LSM6DSV_ACCEL_CONFIG_2 = [self.accel_fs]
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [LSM6DSV_ACCEL_CONFIG_1_REG], LSM6DSV_ACCEL_CONFIG_1)
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [LSM6DSV_ACCEL_CONFIG_2_REG], LSM6DSV_ACCEL_CONFIG_2)

        # Set gyroscope configuration
        LSM6DSV_GYRO_CONFIG_1 = [self.gyro_mode | self.gyro_odr]
        LSM6DSV_GYRO_CONFIG_2 = [self.gyro_fs]
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [LSM6DSV_GYRO_CONFIG_1_REG], LSM6DSV_GYRO_CONFIG_1)
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [LSM6DSV_GYRO_CONFIG_2_REG], LSM6DSV_GYRO_CONFIG_2)

        # Calculate resolutions
        self.accel_res, self.gyro_res = self.__calculate_resolution()

    def calibrate(self):
        '''
        Calibrate the sensor by reading certain number of samples and calculating the average value.
        The average value is then used as the bias for the sensor.
        '''
        sum_values = [0, 0, 0, 0, 0, 0]
        accel_bias = [0, 0, 0]
        gyro_bias = [0, 0, 0]

        for i in range(CALIBRATION_SAMPLES):
            # Read data
            imu_data = self.__read_data()
            for j in range(len(imu_data)):          
                sum_values[j] += imu_data[j]

        calibration_samples_float = float(CALIBRATION_SAMPLES)
        gyro_bias[0] = sum_values[0] * self.gyro_res / calibration_samples_float
        gyro_bias[1] = sum_values[1] * self.gyro_res / calibration_samples_float
        gyro_bias[2] = sum_values[2] * self.gyro_res / calibration_samples_float
        accel_bias[0] = sum_values[3] * self.accel_res / calibration_samples_float
        accel_bias[1] = sum_values[4] * self.accel_res / calibration_samples_float
        accel_bias[2] = sum_values[5] * self.accel_res / calibration_samples_float

        if accel_bias[0] > MAX_ACCEL_BIAS:
            accel_bias[0] -= 1.0  # Remove gravity from the x-axis accelerometer bias calculation
        if accel_bias[0] < MIN_ACCEL_BIAS:
            accel_bias[0] += 1.0  # Remove gravity from the x-axis accelerometer bias calculation
        if accel_bias[1] > MAX_ACCEL_BIAS:
            accel_bias[1] -= 1.0  # Remove gravity from the y-axis accelerometer bias calculation
        if accel_bias[1] < MIN_ACCEL_BIAS:
            accel_bias[1] += 1.0  # Remove gravity from the y-axis accelerometer bias calculation
        if accel_bias[2] > MAX_ACCEL_BIAS:
            accel_bias[2] -= 1.0  # Remove gravity from the z-axis accelerometer bias calculation
        if accel_bias[2] < MIN_ACCEL_BIAS:
            accel_bias[2] += 1.0  # Remove gravity from the z-axis accelerometer bias calculation 

        self.accel_bias = accel_bias
        self.gyro_bias = gyro_bias

    def read(self):
        '''
        Read the data from the sensor and convert it to the correct units.
        '''
        # Read imu data
        imu_data = self.__read_data()

        # Convert data to correct units   
        gx = imu_data[0]*self.gyro_res - self.gyro_bias[0]
        gy = imu_data[1]*self.gyro_res - self.gyro_bias[1]
        gz = imu_data[2]*self.gyro_res - self.gyro_bias[2]

        ax = imu_data[3]*self.accel_res - self.accel_bias[0]
        ay = imu_data[4]*self.accel_res - self.accel_bias[1]
        az = imu_data[5]*self.accel_res - self.accel_bias[2]

        return ((ax, ay, az), (gx, gy, gz))