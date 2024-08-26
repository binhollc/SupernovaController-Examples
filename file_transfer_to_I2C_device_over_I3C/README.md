# Demo: Supernova File Transfer to I2C Device over I3C

This folder contains a demonstration project for interfacing with an I2C FRAM using the Supernova host adapter connected to the I3C High Voltage bus. The project showcases how to load a text file into an I2C FRAM and retrieve the file using Python.

## Introduction

The objective of this project is to load a text file, save it into an I2C FRAM memory, read the I2C FRAM, and store the retrieved data into a new text file for content comparison. Communication with the I2C FRAM is achieved using I3C with legacy I2C device compatibility.

The following flowchart illustrates the process of loading the file and writing the data to the I2C FRAM:

<img src="assets/Write Flowchart.png" alt="write_diagram" width="35%">

The following flowchart illustrates the process of retrieving the data from the I2C FRAM:

<img src="assets/Read Flowchart.png" alt="read_diagram" width="35%">

## Prerequisites

- Python 3.10
- Supernova host adapter
- I2C FRAM connected to the I3C High Voltage bus

<img src="assets/I2C over I3C connection.png" alt="connection_diagram" width="50%">

## Installation

1. **Create and Activate a Virtual Environment:**

   It's recommended to create a virtual environment to manage dependencies.

   - On Windows:

     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   You should now see `(venv)` in your command line, indicating that the virtual environment is active.

2. **Install Dependencies:**

   Use the provided `requirements.txt` file to install the necessary Python packages.

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script using Python:

```bash
# Optional: run if no text file named "Binho_Supernova_Demo.txt" has been created
# python create_demo_text_file.py
python i2c_file_transfer_example.py
```

The script will create a new text file named `I2C_Read_Binho_Supernova_Demo.txt`, which, if everything worked as expected, should contain the same data as the transferred file `Binho_Supernova_Demo.txt`.

You can achieve the same results using the `i2c_file_transfer_example.ipynb` notebook, which provides a step-by-step explanation of the code.
