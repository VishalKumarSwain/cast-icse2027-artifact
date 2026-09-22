import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_da862a11c63a_t {
public boolean openSerialPort(String portName, boolean exclusiveLock) throws SerialPortException {
    // Make sure port is not null
    if (portName == null) {
        throw new SerialPortException(ErrorType.NULL_NOT_PERMITTED);
    }

    // Check if port name corresponds to serial port
    if (serialInterface.getNumberOfSerialPorts() > 0) {
        int serialPortIndex_renamed = serialInterface.serialPortNamesIndex.get(portName).get(serialInterface.serialInterfaceInfo.currentSecurityHandlerIndex);
        if (serialPortIndex_renamed == -1) {
            throw new SerialPortException(ErrorType.INCORRECT_SERIAL_PORT);
        }
    } else {
        throw new SerialPortException(ErrorType.PORT_NOT_FOUND);
    }

    // Make sure port is not already open
    if (portOpened) {
        throw new SerialPortException(ErrorType.PORT_ALREADY_OPENED);
    }

    // Open the port
    int serialPortHandle = serialInterface.openPort(portName, exclusiveLock);

    // Check if error code is invalid
    if (serialPortHandle < 0) {
        switch (serialPortHandle) {
            case SerialPortInterface.PORT_ALREADY_OPENED:
                throw new SerialPortException(ErrorType.PORT_ALREADY_OPENED);
            case SerialPortInterface.PORT_NOT_FOUND:
                throw new SerialPortException(ErrorType.PORT_NOT_FOUND);
            case SerialPortInterface.PERMISSION_DENIED:
                throw new SerialPortException(ErrorType.PERMISSION_DENIED);
            case SerialPortInterface.INCORRECT_SERIAL_PORT:
                throw new SerialPortException(ErrorType.INCORRECT_SERIAL_PORT);
            default:
                throw new SerialPortException(ErrorType.SERIAL_PORT_OPENING_ERROR, serialPortHandle);
        }
    // Handle cases where return value is an invalid handle
    } else if (serialPortHandle != serialInterface.INVALID_HANDLE) {
        portOpened = true;
        return true;
    } else {
        return false;
    }
}

}
