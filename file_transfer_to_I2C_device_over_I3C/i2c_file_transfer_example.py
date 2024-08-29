# Includes
from supernovacontroller.sequential import SupernovaDevice
from BinhoSupernova.commands.definitions import *

## Set up Supernova
# Create an instance of the Supernova class
supernova = SupernovaDevice()

# Open connection to the Supernova device
info = supernova.open()
print(info)

## Load the text file to transfer
print("Load the text file to transfer")
# Read the file contents
with open("./Binho_Supernova_Demo.txt", "r") as file:
    file_content = file.read()

# Convert the content into bytes
file_bytes = file_content.encode('utf-8')

# Create interface to manage the Supernova I3C peripheral as controller
print("Creating interface to manage the Supernova I3C peripheral as controller")
i3c = supernova.create_interface("i3c.controller")

# Setting up I3C bus parameters and initializing the I3C bus
print("Setting up I3C bus parameters and initializing the I3C bus")
i3c.set_parameters(I3cPushPullTransferRate.PUSH_PULL_3_75_MHZ, I2cTransferRate._1MHz)
(success, _) = i3c.init_bus(voltage = 3300)

## Send the data via I3C
print("Start the file transfer")
# Define the value to the 2-byte address auxiliary function
def number_to_bytes(num):
    # Ensure the number fits within 2 bytes
    if num < 0 or num > 0xFFFF:
        raise ValueError("Number out of range for 2 bytes")

    # Convert the number to a 2-byte array
    byte1 = (num >> 8) & 0xFF  # MSB
    byte2 = num & 0xFF         # LSB

    return [byte1, byte2]

# Write the file contents via I3C to the I2C FRAM target
# Initialize variables
package_size = 64
file_length = len(file_bytes)
total_packages = (file_length + package_size - 1) // package_size  # Total packages needed

I2C_FRAM_ADDRESS = 0x50

# Load and send 64-byte arrays
for i in range(total_packages):
    start = i * package_size
    end = start + package_size

    # Convert the starting position to a 2-byte array
    subaddress_array = number_to_bytes(start) 
    
    # Section the text file into a package_size section list
    bytes_to_send = list(file_bytes[start:end])

    # Send the bytes_to_send via I3C 
    (success, _) = i3c.write(target_address = I2C_FRAM_ADDRESS, mode = TransferMode.I2C_MODE, subaddress = subaddress_array, buffer= bytes_to_send)
    
    # Handle errors while writing the 
    if not success:
        # Handle the write failure (e.g., retry or abort)
        print("I2C write failed!")
        break
print("Finished the file transfer")

# Retrieve the FRAM data and store a new text file
print("Move the I2C FRAM memory pointer to address [0x00, 0x00]")
# Move the I2C FRAM memory pointer to address [0x00, 0x00], which is the starting address of the previously stored text file data
(success, _) = i3c.write(target_address = I2C_FRAM_ADDRESS, mode = TransferMode.I2C_MODE,subaddress = [0x00, 0x00], buffer= [])

# Read 30KB worth of data from the I2C FRAM
print("Start the FRAM read")
# Initialize variables
total_bytes_to_read = file_length
read_size = 250
bytes_read = 0
read_data = bytearray()  # To store the data read from  the I2C FRAM

# Loop to read data in 250-byte sections
while bytes_read < total_bytes_to_read:
    # Calculate the remaining bytes
    remaining_bytes = total_bytes_to_read - bytes_read

    # Calculate the amount of bytes to read
    bytes_to_read = min(read_size, remaining_bytes)  
    
    # Read the I2C FRAM memory
    success, data = i3c.read(target_address = I2C_FRAM_ADDRESS,  mode = TransferMode.I2C_MODE, length = bytes_to_read , subaddress = [])
    
    if success:
        # Append the data to the complete read_data bytearray
        read_data.extend(data)
        
        # Update the count of bytes read
        bytes_read += len(data)
    else:
        # Handle the read failure (e.g., retry or abort)
        print("I2C read failed!")
        break
print("Finished the FRAM read")

# Store the read data in the "I2C_Read_Binho_Supernova_Demo.txt" file
print("Store the read data in the 'I2C_Read_Binho_Supernova_Demo.txt' file")
# Write the read data to a new text file in ASCII format
output_file = "./I2C_Read_Binho_Supernova_Demo.txt"
with open(output_file, "w") as file:
    # Convert the bytearray to a string and write to the file
    file.write(read_data.decode('utf-8'))