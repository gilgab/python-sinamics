# Built-in libraries.
import struct
import sys
import time

# Third-party libraries.
import snap7
from snap7.snap7exceptions import Snap7Exception


# Constants and definitions.

# S7 constants when working with SINAMICS via S7
# More info, see:
# gmiru.com/resources/s7proto/constants.txt
AREA = 132  # Code area for Data block (DB)
RACK = 0    # For inverter, only 0 makes sense.
SLOT = 0    # For inverter, only 0 makes sense.

# Struct format characters, more info on:
# https://docs.python.org/2/library/struct.html#format-characters
STRUCT_FORMAT_CHARS = {
                       'c': 1, 'b': 1, 'B': 1, '?': 1,
                       'h': 2, 'H': 2, 'i': 4, 'I': 4,
                       'l': 4, 'L': 4, 'q': 8, 'Q': 8,
                       'f': 4, 'd': 8
                      }

# Constants for reading/writing of U32/Binary parameters (FC00)
# See ***NOTE*** in read_parameter and write_parameter methods.
INDEX0_U32_BINARY = 64512


# Used to return exceptions for a few user erroneous arguments cases.
class SinamicsException(Exception):
    pass


# Sinamics Class definition.

class Sinamics():

    """ Class for Sinamics control/monitoring.

    The read/write requests are based in the article of
    number (Entry ID) 97550333 in the SIOS website
    (Siemens Industry Online Support).

    """
    def __init__(self):
        # Defining this object as a S7 Client.
        # See: snap7.sourceforge.net/home.html

        self.converter = snap7.client.Client()

    def destroy(self,):
        """ This method can be used to destroy the snap7 client.

        """

        self.converter.destroy()

    def connect(self, ip_address):
        """ This method can be used to establish connection
        to the inverter. It should be your second call after object init.

        ARGUMENTS
        -----------
        - ip_address is the IP of the inverter you are trying to connect to.

        """

        # Trying to connect.
        self.converter.connect(ip_address, RACK, SLOT)

    def disconnect(self):
        """ This method can be used to disconnect from inverter.
        """

        self.converter.disconnect()

    def read_parameter(self, number, data_type,
                       index=0, drive_object=1, no_unpack=False):
        """ This method can be used to read any parameter in the inverter.

        ARGUMENTS
        -----------
        - number is the parameter number, e.g., reading r0026, number=26.
        - data_type is the type of parameter data, e.g.,
          r0026 is floating32, so data_type='f'.
          A list of data_types characters can be seen in
          https://docs.python.org/2/library/struct.html#format-characters
          Description of a parameter data type can be seen in the List Manual.
        - index is the parameter index, e.g., reading r0722.1, index=1.
        - drive_object is the drive object number (for g120 is always 1).
        - no_unpack equal True means that the raw hex value of the parameter
          will be read, with no struct library unpack.

        RETURNS
        -----------
        The parameter value in human-readable form with no_unpack=False,
        or in hexadecimal value with no_unpack=True.

        EXAMPLE 1
        -----------
        Reading the link DC, r0026, of g120 inverter (should be something
        around 1.35*VL, with VL being the AC line voltage of inverter infeed).
        As List manual describes, r0026 is a float32 and with index 0 only.

        import sinamics

        g120 = sinamics.Sinamics()
        g120.connect('192.168.0.20')
        VDC = g120.read_parameter(26, 'f')

        ***NOTE***
        -----------
        REGARDING READ/WRITE OF PARAMETER WITH
        DATA TYPE U32/Binary (P0840, P0844, etc.) OR
        DATA TYPE U32/Floating32 (P1070, etc.).

        Parameters with this data type are tricky to read and write.
        The data type informed must be 'I/B'.
        It is formed by 4 bytes:
        First 2 bytes from left to right --> main value or parameter number.
        Last 2 bytes from left to right  --> bit to be taken from (i.e index).
        For last 2 bytes, a value of FC00 means bit 0, FC01 means bit 1, etc.

        EXAMPLE 2
        -----------
        Reading P0840 with P0840 = 2090.0 returns (using unpack regarding 'I',
        Unsigned32, and converting from little endian to big endian):
        In Decimal; 137034752
        In Hexadecimal; 082A FC00 ->>
        - 082A in Decimal means 2090;
        - FC00 in Decimal measn 64512 and is the correspondent to index 0.

        """

        offset = 1024*drive_object + index  # Defined in SIOS article 97550333
        # Here is where the reading actually occurs.
        # data_type[0] to take 'I' in 'I/B' cases (see ***NOTE***).
        data = self.converter.read_area(AREA, number, offset,
                                        STRUCT_FORMAT_CHARS[data_type[0]])

        if no_unpack:
            # Return raw hex value.
            return data

        else:
            # The hex read value is unpacked and converted
            # from little endian to big endian.
            # data_type[0] exists to take 'I' in 'I/B' cases (see ***NOTE***)
            data = struct.unpack(data_type[0], data[::-1])[0]

            # See ***NOTE*** in method comments.
            if data_type == 'I/B':
                data = hex(data).split('x')[-1]  # Removing 0x from hex.
                n_nibbles = 8                    # Nibbles in 4 bytes.

                # Adding zeros at start, otherwise will not display 4 bytes.
                if len(data) < n_nibbles:
                    data = (n_nibbles - len(data))*'0' + data

                # Taking the reading of 'r722.0' as example:
                first_val = str(int(data[0:4], 16))    # first_val is 722.
                last_val = str((int(data[4:8], 16)
                                - INDEX0_U32_BINARY))  # last_val is 0.
                point = '.'                            # Separator.

                # In case the last two bytes are lower than INDEX0_U32_BINARY
                # It means, for U32/Binary or U32/float32 data type parameters,
                # That the reading should return a value or parameter,
                # With no relevant value in the last two bytes.
                if int(data[4:8], 16) < INDEX0_U32_BINARY:
                    last_val = point = ''

                # Final display.
                data = first_val + point + last_val

            return data

    def write_parameter(self, number, value,
                        data_type, index=0, drive_object=1):
        """ This method can be used to write a value to a
        SINAMICS inverter parameter. The data type of the
        parameter to be write must be know. If the writing
        fails an exception is raised by python-sinamics snap7.

        ARGUMENTS:
        -----------
        - number is the parameter number to be written, e.g., writing P1121.
        - value is the value to be written to parameter e.g.,
          writing P1121 equal to 10 seconds, value=10.
        - data_type is the type of parameter data, e.g.,
          r0026 floating32, so data_type='f'.
          A complete list of data_types characters can be seen in
          https://docs.python.org/2/library/struct.html#format-characters
          Description of a parameter data type can be seen in the List Manual.
        - index is the index of the parameter to be write.
          E.g., writing P0756[01] = 3, index=1.
        - drive_object is the drive object number (for g120 is always 1).

        EXAMPLE 1
        -----------
        Writing 1800 rpm to P2000:

        g120.write(2000, 1800., 'f')

        ***NOTE***
        -----------
        REGARDING READ/WRITE OF PARAMETER WITH
        DATA TYPE U32/Binary (P0840, P0844, etc.) OR
        DATA TYPE U32/Floating32 (P1070, etc.).

        Parameters with this data type are tricky to read and write.
        The data type informed must be 'I/B'.
        It is formed by 4 bytes:
        First 2 bytes from left to right --> main value or parameter number.
        Last 2 bytes from left to right  --> bit to be taken from (i.e index).
        For last 2 bytes, a value of FC00 means bit 0, FC01 means bit 1, etc.

        The same structure is used to facilitate writing
        values to U32/Binary and U32/Float32 parameters.
        A '.' must always be present when writing a BICO
        parameter as 'value' argument.

        EXAMPLE 2
        -----------
        Reading P0840 with P0840 = 2090.0 returns (using unpack regarding 'I',
        Unsigned32, and converting from little endian to big endian):

        In Decimal; 137034752
        In Hexadecimal; 082A FC00 ->>
        - 082A in Decimal means 2090;
        - FC00 in Decimal measn 64512 and is the correspondent to index 0.

        EXAMPLE 3
        -----------
        Writing P1113 = r2092.2 and P1070 = r0755.1:

        g120.write(1113, '2092.2', 'I/B')
        g120.write(1070, '755.1', 'I/B')

        """

        offset = 1024*drive_object + index  # Defined in SIOS article 97550333

        # see ***NOTE*** in comments above.
        if data_type == 'I/B':
            # Tratative to take strings 'value' with parameter + '.' + index
            # To be written to desired parameter ('number' argument).
            # e.g. writting r722.2 to P0844:
            # value = '722.2'.

            # If you wish to write 0 or 1 directly to the parameter
            # Defined in 'number', value can be informed as int.

            # Text to raise exception in wrong 'value' cases.
            text = """ Argument 'value' is in incorrect format!
            If you are trying to write a U32/binary parameter,
            the value to be written should be:
            - 0 or 1 (int accepted);
            - a string containing BICO parameter number + '.' + index,
              E.g. for writing r722.2 to P0844:
              inverter.write_parameter(844, '722.2', 'I/B').
            """

            if type(value) is int:
                # In case value is 0 or 1.
                if value == 0 or value == 1:
                    # 2**16 to indicate the value is rotating left two bytes.
                    value = (2**16)*int(value)
                else:
                    # If it reaches here, an incorrect 'value' was informed.
                    raise SinamicsException(text)

            elif type(value) is str:
                # In case it's a string defining other BICO parameter.
                if '.' not in value:
                    # If it reaches here, an incorrect 'value' was informed.
                    raise SinamicsException(text)
                value = value.split('.')
                # 2**16 to indicate the value is rotating left two bytes.
                value = (int(value[0])*(2**16)
                         + int(value[1])
                         + INDEX0_U32_BINARY)

            else:
                # Neither String or Int value was informed.
                raise SinamicsException(text)

        # data_type[0] to take 'I' in 'I/B' cases (see ***NOTE***).
        value = bytearray(struct.pack(data_type[0], value))
        # Where the writing actually occurs.
        self.converter.write_area(AREA, number, offset, value[::-1])

    def get_req_time(self, param=None, drive_object=1):
        """ This method can be used to check the response time of a 2 byte
        read request in miliseconds. Should be seem as a basic measure
        of how much time a request takes.

        ARGUMENTS
        -----------
        - param is an optional argument. It should be a list containing the
          arguments as a read_parameter method request.
          It defines which parameter will be used in the request attempt.
        - drive_object can be defined case you want to read the
          request time using default for a different drive_object.

        RETURNS
        -----------
        - Returns the time taken to complete the request in miliseconds.

        EXAMPLE 1
        -----------
        g120.request_time() # OR
        g120.request_time([26, 'f']) # using 4 byte request - DC link

        By default, this method tries to read r0002 from the inverter,
        since it's a parameter that exist in most inverters and drive objects.

        """

        if type(param) is list:
            start = time.time()
            self.read_parameter(*param)
            end = time.time()

        else:
            # If reading *param fails, we try the default r0002.
            start = time.time()
            self.read_parameter(2, 'h', drive_object=drive_object)
            end = time.time()

        return (end - start)*1000.0  # Converting from seconds to ms.

    def get_param_list(self, filepath, max_param, DO_numbers):
        """ This method can be used to search for all parameters
        that get a response from S7 requests. A txt file is generated
        with the list for each drive object specified. Only the parameters
        that got a read response are saved, there is no interest in the value.

        ARGUMENTS
        -----------
        - filepath is the the path where the txt files will be saved.
        - max_param is the maximum parameter to be searched for.
        - DO_numbers is a list containing each drive object to be searched.

        """

        # Adding / to end of filepath if it does not have.
        if filepath[-1] != '/':
            filepath += '/'

        # Opening txt files
        txtfiles = [0 for i in range(0, len(DO_numbers))]
        for i in range(0, len(DO_numbers)):
            txtfiles[i] = open('{}params_DO{}.txt'.format(filepath,
                                                          DO_numbers[i]), 'w')
            text = ("""Parameters with response """
                    """using DO equal {}\n""").format(DO_numbers[i])
            txtfiles[i].write(text)  # Text file header

        # Searching for read request responses
        param = 0  # counter
        while param < max_param:
            for i in range(0, len(DO_numbers)):
                try:
                    # Try to read, if don't work, goes to next DO.
                    self.read_parameter(param, 'I', drive_object=DO_numbers[i])
                    txtfiles[i].write(str(param)+'\n')
                except:
                    pass
            param += 1

        # Closing text files
        for item in txtfiles:
            item.close()
