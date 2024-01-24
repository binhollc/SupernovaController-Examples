import matplotlib.pyplot as plt
import time
from supernovacontroller.sequential import SupernovaDevice
from definitions import *
from ctypes import *

def find_matching_item(data, target_pid):
    for item in data:
        if item.get('pid') == target_pid:
            return item
    return None

class LSM6DSV:
    pid = [0x02, 0x08, 0x00, 0x70, 0x92, 0x0B]
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

    def _calculate_resolution(self):
        '''
        Calculate the resolutions of the sensor based on the current configuration.
        Use the respective full scale values and the number of bits (16) to calculate the resolutions.
        '''
        a_res = LSM6DSV_ACCEL_FS_VALUES[self.accel_fs] / LSM6DSV_ACCEL_RESOLUTION
        g_res = LSM6DSV_GYRO_FS_VALUES[self.gyro_fs] / LSM6DSV_GYRO_RESOLUTION

        return (a_res, g_res)
    
    def _read_data(self):
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
        self.accel_res, self.gyro_res = self._calculate_resolution()

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
            imu_data = self._read_data()
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
        imu_data = self._read_data()

        # Convert data to correct units   
        gx = imu_data[0]*self.gyro_res - self.gyro_bias[0]
        gy = imu_data[1]*self.gyro_res - self.gyro_bias[1]
        gz = imu_data[2]*self.gyro_res - self.gyro_bias[2]

        ax = imu_data[3]*self.accel_res - self.accel_bias[0]
        ay = imu_data[4]*self.accel_res - self.accel_bias[1]
        az = imu_data[5]*self.accel_res - self.accel_bias[2]

        return ((ax, ay, az), (gx, gy, gz))

def main():
    device = SupernovaDevice()

    info = device.open()

    print(info)

    i3c = device.create_interface("i3c.controller")

    i3c.set_parameters(i3c.I3cPushPullTransferRate.PUSH_PULL_12_5_MHZ, i3c.I3cOpenDrainTransferRate.OPEN_DRAIN_4_17_MHZ)
    (success, _) = i3c.init_bus(3300)

    if not success:
        print("I couldn't initialize the bus. Are you sure there's any target connected?")
        exit(1)

    (_, targets) = i3c.targets()

    sensor = LSM6DSV(i3c)

    sensor.init_device()

    sensor.calibrate()

    # Setup the matplotlib figure and axes
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle('Supernova with LSM6DSV Device Demo', fontsize=16)
    plt.get_current_fig_manager().set_window_title("Sensor Data Visualization")

    # Initialize lists to store the data
    times = []
    acc_data = {'x': [], 'y': [], 'z': []}
    gyro_data = {'x': [], 'y': [], 'z': []}

    start_time = time.time()

    keep_running = True

    def on_key(event):
        nonlocal keep_running
        if event.key == 'q':
            keep_running = False

    fig.canvas.mpl_connect('key_press_event', on_key)

    while keep_running:
        current_time = time.time() - start_time
        times.append(current_time)

        # Read data from sensor
        (acc, gyro) = sensor.read()

        # Update accelerometer data
        acc_data['x'].append(acc[0])
        acc_data['y'].append(acc[1])
        acc_data['z'].append(acc[2])

        # Update gyroscope data
        gyro_data['x'].append(gyro[0])
        gyro_data['y'].append(gyro[1])
        gyro_data['z'].append(gyro[2])

        # Plot accelerometer data
        ax1.cla()
        ax1.plot(times, acc_data['x'], label='X')
        ax1.plot(times, acc_data['y'], label='Y')
        ax1.plot(times, acc_data['z'], label='Z')
        ax1.legend()
        ax1.set_title('Accelerometer Data')
        ax1.set_ylabel('Acceleration (g)')

        # Plot gyroscope data
        ax2.cla()
        ax2.plot(times, gyro_data['x'], label='X')
        ax2.plot(times, gyro_data['y'], label='Y')
        ax2.plot(times, gyro_data['z'], label='Z')
        ax2.legend()
        ax2.set_title('Gyroscope Data')
        ax2.set_ylabel('Angular Velocity (dps)')

        plt.pause(0.1)

        # Limit the size of the data lists
        if len(times) > 50:
            times.pop(0)
            for data_list in acc_data.values():
                data_list.pop(0)
            for data_list in gyro_data.values():
                data_list.pop(0)

    plt.close(fig)

    device.close()

if __name__ == "__main__":
    main()