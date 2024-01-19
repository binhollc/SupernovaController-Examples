from enum import Enum

BMI323_ACCEL_CONFIG_REG = 0x20

class BMI323_ACCEL_OP_MODES(Enum):
    SUSPEND          = 0x00
    LOW_POWER_MODE   = 0x30
    HIGH_PERFORMANCE = 0x40
    NORMAL           = 0x70

class BMI323_ACCEL_AVG_NUM(Enum):
    NO_AVG = 0x00
    AVG_2  = 0x01
    AVG_4  = 0x02
    AVG_8  = 0x03
    AVG_16 = 0x04
    AVG_32 = 0x05
    AVG_64 = 0x06

class BMI323_ACCEL_FILTER_BW(Enum):
    ODR_2  = 0x00
    ODR_4  = 0x80

class BMI323_ACCEL_FS(Enum):
    FS_2g   = 0x00
    FS_4g   = 0x10
    FS_8g   = 0x20
    FS_16g  = 0x30

BMI323_ACCEL_FS_VALUES = {
    BMI323_ACCEL_FS.FS_2g.value:   2.0,
    BMI323_ACCEL_FS.FS_4g.value:   4.0,
    BMI323_ACCEL_FS.FS_8g.value:   8.0,
    BMI323_ACCEL_FS.FS_16g.value:  16.0
}

class BMI323_ACCEL_ODR(Enum):
    AODR_0_78125Hz  = 0x01
    AODR_1_5625Hz   = 0x02
    AODR_3_125Hz    = 0x03
    AODR_6_25Hz     = 0x04
    AODR_12_5Hz     = 0x05
    AODR_25Hz       = 0x06
    AODR_50Hz       = 0x07
    AODR_100Hz      = 0x08
    AODR_200Hz      = 0x09
    AODR_400Hz      = 0x0A
    AODR_800Hz      = 0x0B
    AODR_1_6kHz     = 0x0C
    AODR_3_2kHz     = 0x0D
    AODR_6_4kHz     = 0x0E

BMI323_GYRO_CONFIG_REG = 0x21

class BMI323_GYRO_OP_MODES(Enum):
    SUSPEND          = 0x00
    DRIVER_ONLY      = 0x10
    LOW_POWER_MODE   = 0x30
    HIGH_PERFORMANCE = 0x40
    NORMAL           = 0x70

class BMI323_GYRO_AVG_NUM(Enum):
    NO_AVG = 0x00
    AVG_2  = 0x01
    AVG_4  = 0x02
    AVG_8  = 0x03
    AVG_16 = 0x04
    AVG_32 = 0x05
    AVG_64 = 0x06

class BMI323_GYRO_FILTER_BW(Enum):
    ODR_2  = 0x00
    ODR_4  = 0x80

class BMI323_GYRO_ODR(Enum):
    GODR_0_78125Hz  = 0x01
    GODR_1_5625Hz   = 0x02
    GODR_3_125Hz    = 0x03
    GODR_6_25Hz     = 0x04
    GODR_12_5Hz     = 0x05
    GODR_25Hz       = 0x06
    GODR_50Hz       = 0x07
    GODR_100Hz      = 0x08
    GODR_200Hz      = 0x09
    GODR_400Hz      = 0x0A
    GODR_800Hz      = 0x0B
    GODR_1_6kHz     = 0x0C
    GODR_3_2kHz     = 0x0D
    GODR_6_4kHz     = 0x0E

class BMI323_GYRO_FS(Enum):
    FS_125dps   = 0x00
    FS_250dps   = 0x10
    FS_500dps   = 0x20
    FS_1000dps  = 0x30
    FS_2000dps  = 0x40

BMI323_GYRO_FS_VALUES = {
    BMI323_GYRO_FS.FS_125dps.value:  125.0,
    BMI323_GYRO_FS.FS_250dps.value:  250.0,
    BMI323_GYRO_FS.FS_500dps.value:  500.0,
    BMI323_GYRO_FS.FS_1000dps.value: 1000.0,
    BMI323_GYRO_FS.FS_2000dps.value: 2000.0
}

BMI323_ACCEL_DATA_X = 0x03