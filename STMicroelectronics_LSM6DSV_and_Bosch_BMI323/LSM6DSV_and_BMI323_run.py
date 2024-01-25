import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Bosch_BMI323.BMI323 import BMI323
from STMicroelectronics_LSM6DSV.LSM6DSV import LSM6DSV
from supernovacontroller.sequential import SupernovaDevice
import matplotlib.pyplot as plt
import time

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

    sensor_bmi323 = BMI323(i3c)

    sensor_lsm6dsv = LSM6DSV(i3c)

    sensor_bmi323.init_device()

    sensor_lsm6dsv.init_device()

    sensor_bmi323.calibrate()

    sensor_lsm6dsv.calibrate()

    # Setup the matplotlib figure and axes
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle('Supernova with BMI323 Device Demo', fontsize=16)
    plt.get_current_fig_manager().set_window_title("Sensor Data Visualization")

    fig2, (ax21, ax22) = plt.subplots(2, 1)
    fig2.subplots_adjust(hspace=0.5)
    fig2.suptitle('Supernova with LSM6DSV Device Demo', fontsize=16)

    # Initialize lists to store the data
    times = []
    acc_data_bmi323 = {'x': [], 'y': [], 'z': []}
    gyro_data_bmi323 = {'x': [], 'y': [], 'z': []}

    acc_data_lsm6dsv = {'x': [], 'y': [], 'z': []}
    gyro_data_lsm6dsv = {'x': [], 'y': [], 'z': []}

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

        # Read data from sensors
        (acc_bmi323, gyro_bmi323) = sensor_bmi323.read()
        (acc_lsm6dsv, gyro_lsm6dsv) = sensor_lsm6dsv.read()

        # Update accelerometers data
        acc_data_bmi323['x'].append(acc_bmi323[0])
        acc_data_bmi323['y'].append(acc_bmi323[1])
        acc_data_bmi323['z'].append(acc_bmi323[2])

        acc_data_lsm6dsv['x'].append(acc_lsm6dsv[0])
        acc_data_lsm6dsv['y'].append(acc_lsm6dsv[1])
        acc_data_lsm6dsv['z'].append(acc_lsm6dsv[2])

        # Update gyroscopes data
        gyro_data_bmi323['x'].append(gyro_bmi323[0])
        gyro_data_bmi323['y'].append(gyro_bmi323[1])
        gyro_data_bmi323['z'].append(gyro_bmi323[2])

        gyro_data_lsm6dsv['x'].append(gyro_lsm6dsv[0])
        gyro_data_lsm6dsv['y'].append(gyro_lsm6dsv[1])
        gyro_data_lsm6dsv['z'].append(gyro_lsm6dsv[2])

        # Plot accelerometers data
        ax1.cla()
        ax1.plot(times, acc_data_bmi323['x'], label='X')
        ax1.plot(times, acc_data_bmi323['y'], label='Y')
        ax1.plot(times, acc_data_bmi323['z'], label='Z')
        ax1.legend()
        ax1.set_title('Accelerometer Data')
        ax1.set_ylabel('Acceleration (g)')

        ax21.cla()
        ax21.plot(times, acc_data_lsm6dsv['x'], label='X')
        ax21.plot(times, acc_data_lsm6dsv['y'], label='Y')
        ax21.plot(times, acc_data_lsm6dsv['z'], label='Z')
        ax21.legend()   
        ax21.set_title('Accelerometer Data')    
        ax21.set_ylabel('Acceleration (g)')

        # Plot gyroscopes data
        ax2.cla()
        ax2.plot(times, gyro_data_bmi323['x'], label='X')
        ax2.plot(times, gyro_data_bmi323['y'], label='Y')
        ax2.plot(times, gyro_data_bmi323['z'], label='Z')
        ax2.legend()
        ax2.set_title('Gyroscope Data')
        ax2.set_ylabel('Angular Velocity (dps)')

        ax22.cla()
        ax22.plot(times, gyro_data_lsm6dsv['x'], label='X')
        ax22.plot(times, gyro_data_lsm6dsv['y'], label='Y')
        ax22.plot(times, gyro_data_lsm6dsv['z'], label='Z')
        ax22.legend()
        ax22.set_title('Gyroscope Data')
        ax22.set_ylabel('Angular Velocity (dps)')

        plt.pause(0.1)

        # Limit the size of the data lists
        if len(times) > 50:
            times.pop(0)
            for data_list in acc_data_bmi323.values():
                data_list.pop(0)
            for data_list in gyro_data_bmi323.values():
                data_list.pop(0)
            for data_list in acc_data_lsm6dsv.values():
                data_list.pop(0)
            for data_list in gyro_data_lsm6dsv.values():
                data_list.pop(0)

    plt.close(fig)

    device.close()

if __name__ == "__main__":
    main()