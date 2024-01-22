from enum import Enum

# Address of the LSM6DSV Accelerometer Configuration 1 Register
LSM6DSV_ACCEL_CONFIG_1_REG = 0x10

class LSM6DSV_ACCEL_OP_MODES(Enum):
    """Accelerometer operating modes"""
    HIGH_PERFORMANCE = 0x00
    HIGH_ACCURACY    = 0x10
    ODR_TRIGGERED    = 0x30
    LPM_1            = 0x40
    LPM_2            = 0x50
    LPM_3            = 0x60
    NORMAL           = 0x70

class LSM6DSV_ACCEL_ODR(Enum):
    """Accelerometer output data rates"""
    POWER_DOWN      = 0x00
    AODR_1_875Hz    = 0x01
    AODR_7_5Hz      = 0x02
    AODR_15Hz       = 0x03
    AODR_30Hz       = 0x04
    AODR_60Hz       = 0x05
    AODR_120Hz      = 0x06
    AODR_240Hz      = 0x07
    AODR_480Hz      = 0x08
    AODR_960Hz      = 0x09
    AODR_1_92kHz    = 0x0A
    AODR_3_84kHz    = 0x0B
    AODR_7_68kHz    = 0x0C

# Address of the LSM6DSV Accelerometer Configuration 2 Register
LSM6DSV_ACCEL_CONFIG_2_REG = 0x17

class LSM6DSV_ACCEL_FS(Enum):
    """Accelerometer full scale values"""
    FS_2g   = 0x00
    FS_4g   = 0x01
    FS_8g   = 0x02
    FS_16g  = 0x03

# Accelerometer full scale values in g
LSM6DSV_ACCEL_FS_VALUES = {
    LSM6DSV_ACCEL_FS.FS_2g.value:   2.0,
    LSM6DSV_ACCEL_FS.FS_4g.value:   4.0,
    LSM6DSV_ACCEL_FS.FS_8g.value:   8.0,
    LSM6DSV_ACCEL_FS.FS_16g.value:  16.0
}

# Accelerometer 16 bits symmetric resolution
LSM6DSV_ACCEL_RESOLUTION = 32768.0

# Address of the LSM6DSV Gyroscope Configuration 1 Register
LSM6DSV_GYRO_CONFIG_1_REG = 0x11

class LSM6DSV_GYRO_OP_MODES(Enum):
    """Gyroscope operating modes"""
    HIGH_PERFORMANCE = 0x00
    HIGH_ACCURACY    = 0x10
    ODR_TRIGGERED    = 0x30
    SLEEP            = 0x40
    LPM              = 0x50

class LSM6DSV_GYRO_ODR(Enum):
    """Gyroscope output data rates"""
    POWER_DOWN      = 0x00
    GODR_7_5Hz      = 0x02
    GODR_15Hz       = 0x03
    GODR_30Hz       = 0x04
    GODR_60Hz       = 0x05
    GODR_120Hz      = 0x06
    GODR_240Hz      = 0x07
    GODR_480Hz      = 0x08
    GODR_960Hz      = 0x09
    GODR_1_92kHz    = 0x0A
    GODR_3_84kHz    = 0x0B
    GODR_7_68kHz    = 0x0C

# Address of the LSM6DSV Gyroscope Configuration 2 Register
LSM6DSV_GYRO_CONFIG_2_REG = 0x15

class LSM6DSV_GYRO_FS(Enum):
    """Gyroscope full scale values"""
    FS_125dps   = 0x00
    FS_250dps   = 0x01
    FS_500dps   = 0x02
    FS_1000dps  = 0x03
    FS_2000dps  = 0x04
    FS_4000dps  = 0x0C

# Gyroscope full scale values in dps
LSM6DSV_GYRO_FS_VALUES = {
    LSM6DSV_GYRO_FS.FS_125dps.value:  125.0,
    LSM6DSV_GYRO_FS.FS_250dps.value:  250.0,
    LSM6DSV_GYRO_FS.FS_500dps.value:  500.0,
    LSM6DSV_GYRO_FS.FS_1000dps.value: 1000.0,
    LSM6DSV_GYRO_FS.FS_2000dps.value: 2000.0,
    LSM6DSV_GYRO_FS.FS_4000dps.value: 4000.0
}

# Gyroscope data X register address
LSM6DSV_GYRO_DATA_X = 0x22

# Gyroscope 16 bits symmetric resolution
LSM6DSV_GYRO_RESOLUTION = 32768.0