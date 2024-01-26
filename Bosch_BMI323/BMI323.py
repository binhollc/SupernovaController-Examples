import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from BMI323_definitions import *
from ctypes import *

# The read method needs to read two dummy bytes before the actual data
# as specified in the BMI323 datasheet
OFFSET_FOR_DUMMY_BYTES = 2

def find_matching_item(data, target_pid):
    for item in data:
        if item.get('pid') == target_pid:
            return item
    return None

class BMI323:
    pid = [0x07, 0x70, 0x10, 0x43, 0x10, 0x00]
    address = None

    # Sensor configuration
    accel_mode = BMI323_ACCEL_OP_MODES.HIGH_PERFORMANCE.value
    accel_avg_num = BMI323_ACCEL_AVG_NUM.NO_AVG.value
    accel_filter_bw = BMI323_ACCEL_FILTER_BW.ODR_4.value
    accel_fs = BMI323_ACCEL_FS.FS_2g.value
    accel_odr = BMI323_ACCEL_ODR.AODR_100Hz.value
    
    gyro_mode = BMI323_GYRO_OP_MODES.HIGH_PERFORMANCE.value
    gyro_avg_num = BMI323_GYRO_AVG_NUM.NO_AVG.value
    gyro_filter_bw = BMI323_GYRO_FILTER_BW.ODR_4.value
    gyro_fs = BMI323_GYRO_FS.FS_250dps.value
    gyro_odr = BMI323_GYRO_ODR.GODR_100Hz.value

    # Calibration
    accel_bias = None
    gyro_bias = None

    def __init__(self, i3c):
        self.i3c = i3c

        (_, targets) = i3c.targets()

        bmi_device = find_matching_item(targets, self.pid)

        if bmi_device is None:
            print("BMI device not found in the I3C bus")
            return
        
        self.address = bmi_device["dynamic_address"]

    def __calculate_resolutions(self):
        '''
        Calculate the resolutions of the sensor based on the current configuration.
        Use the respective full scale values and the number of bits (16) to calculate the resolutions.
        '''
        a_res = BMI323_ACCEL_FS_VALUES[self.accel_fs] / BMI323_ACCEL_RESOLUTION
        g_res = BMI323_GYRO_FS_VALUES[self.gyro_fs] / BMI323_GYRO_RESOLUTION
        return (a_res, g_res)

    def __read_data(self):
        '''
        Read the data from the sensor. The data is read in a single transaction starting from the
        accelerometer data X register. The data is then converted to signed 16-bit integers.
        '''
        # The three components of the accelerometer and gyroscope are 2-bytes length each
        READ_LEN = 12

        # Read data
        (_, raw_data) = self.i3c.read(self.address, self.i3c.TransferMode.I3C_SDR, [BMI323_ACCEL_DATA_X], OFFSET_FOR_DUMMY_BYTES + READ_LEN)
        
        # Convert data to signed 16-bit integers
        imu_data = [0, 0, 0, 0, 0, 0]
        for i in range(len(imu_data)):
            imu_data[i] = c_int16((raw_data[OFFSET_FOR_DUMMY_BYTES + 2*i + 1] << 8) | raw_data[OFFSET_FOR_DUMMY_BYTES + 2*i]).value
        
        return imu_data
    
    def init_device(self):
        '''
        Initialize the sensor with the current configuration. Uses two words of 16 bits to write the
        configuration, one for the accelerometer and one for the gyroscope.
        '''
        # Set accelerometer configuration
        BMI323_ACCEL_CONFIG_LB = self.accel_filter_bw | self.accel_fs | self.accel_odr
        BMI323_ACCEL_CONFIG_HB = self.accel_mode | self.accel_avg_num
        BMI323_ACCEL_CONFIG = [BMI323_ACCEL_CONFIG_LB, BMI323_ACCEL_CONFIG_HB]
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [BMI323_ACCEL_CONFIG_REG], BMI323_ACCEL_CONFIG)
        
        # Set gyroscope configuration
        BMI323_GYRO_CONFIG_LB = self.gyro_filter_bw | self.gyro_fs | self.gyro_odr
        BMI323_GYRO_CONFIG_HB = self.gyro_mode | self.gyro_avg_num
        BMI323_GYRO_CONFIG = [BMI323_GYRO_CONFIG_LB, BMI323_GYRO_CONFIG_HB]
        self.i3c.write(self.address, self.i3c.TransferMode.I3C_SDR, [BMI323_GYRO_CONFIG_REG], BMI323_GYRO_CONFIG)
        
        # Calculate resolutions
        self.accel_res, self.gyro_res = self.__calculate_resolutions()

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
        accel_bias[0] = sum_values[0] * self.accel_res / calibration_samples_float
        accel_bias[1] = sum_values[1] * self.accel_res / calibration_samples_float
        accel_bias[2] = sum_values[2] * self.accel_res / calibration_samples_float
        gyro_bias[0] = sum_values[3] * self.gyro_res / calibration_samples_float
        gyro_bias[1] = sum_values[4] * self.gyro_res / calibration_samples_float
        gyro_bias[2] = sum_values[5] * self.gyro_res / calibration_samples_float

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
        ax = imu_data[0]*self.accel_res - self.accel_bias[0]
        ay = imu_data[1]*self.accel_res - self.accel_bias[1]
        az = imu_data[2]*self.accel_res - self.accel_bias[2]

        gx = imu_data[3]*self.gyro_res - self.gyro_bias[0]
        gy = imu_data[4]*self.gyro_res - self.gyro_bias[1]
        gz = imu_data[5]*self.gyro_res - self.gyro_bias[2]

        return ((ax, ay, az), (gx, gy, gz))