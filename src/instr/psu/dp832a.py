class DP832A:
    def __init__(self, rm, ip, init=True):
        self.inst = rm.open_resource(f"TCPIP::{ip}::INSTR")
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        if init:
            self.init()

    def about(self):
        """
        Returns information about the power supply.
        """
        try:
            idn = self.inst.query("*IDN?").split(',')
        except Exception as e:
            print(f"Error querying IDN: {e}")
        else:
            return {
                "manufacturer": idn[0],
                "model": idn[1],
                "serial": idn[2],
                "firmware": idn[3],
            }
    

    def status(self):
        """
        Get the status of all channels. 
        """
        res = {}
        for ch in range(1, 4):
            try:
                ch_status = self.inst.query(f':OUTP? CH{ch}').strip()
                voltage = self.inst.query(f':MEAS:VOLT? CH{ch}').strip()
                current = self.inst.query(f':MEAS:CURR? CH{ch}').strip()
                ovp = self.inst.query(f':OUTP:OVP:VAL? CH{ch}').strip()
                ocp = self.inst.query(f':OUTP:OCP:VAL? CH{ch}').strip()
                ovp_status = self.inst.query(f':OUTP:OVP? CH{ch}').strip()
                ocp_status = self.inst.query(f':OUTP:OCP? CH{ch}').strip()
                mode = self.get_mode(ch)
                
            except Exception as e:
                print(f"Error querying status for CH{ch}: {e}")
            else:
                res[f'CH{ch}'] = {
                    'output_status': ch_status,
                    'voltage': voltage,
                    'current': current,
                    'ovp_limit': ovp,
                    'ocp_limit': ocp,
                    'ovp_status': ovp_status,
                    'ocp_status': ocp_status,
                    'mode': mode,
                }
        return res


    def set_function(self, channel: int, function_type: str, value: int):
        """
        Set the voltage or current limit for a channel, in mV/mA. Returns the set value if successful.
            channel: 1, 2, or 3
            function_type: "voltage" or "current"
            value: value in mV (for voltage) or mA (for current)
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if function_type not in ["voltage", "current"]:
            raise ValueError("Invalid function type. Use 'voltage' or 'current'.")
        
        if function_type == "voltage":
            if channel == 3 and (value > 5000 or value < 0):
                raise ValueError("Voltage for CH3 must be between 0mV and 5000 mV")
            if channel in [1, 2] and (value > 30000 or value < 0):
                raise ValueError("Voltage for CH1 and CH2 must be between 0mV and 30000 mV")
        elif function_type == "current":
            if value > 3000 or value < 0:
                raise ValueError("Current must be between 0mA and 3000 mA") 

        voltage = self.inst.query(f':APPL? CH{channel}, VOLT')
        current = self.inst.query(f':APPL? CH{channel}, CURR')

        try:
            if function_type == "voltage":
                self.inst.write(f':APPL CH{channel},{value/1000},{current}')
            elif function_type == "current":
                self.inst.write(f':APPL CH{channel},{voltage},{value/1000}')
        except Exception as e:
            print(f"Error setting CH{channel} {function_type} to {value}: {e}")
        finally:
            res = self.inst.query(f':APPL? CH{channel}')
            if function_type == "voltage" and float(res.split(',')[1]) * 1000 != value:
                raise RuntimeError(f"Failed to set CH{channel} voltage to {value}: {res}")
            elif function_type == "current" and float(res.split(',')[2]) * 1000 != value:
                raise RuntimeError(f"Failed to set CH{channel} current to {value}: {res}")
            else:
                if function_type == "voltage":
                    return float(res.split(',')[1]) * 1000
                elif function_type == "current":
                    return float(res.split(',')[2]) * 1000


    def set_protection(self, channel: int, protection_type: str, value: int):
        """
        Set the overvoltage or overcurrent protection for a channel, in mV/mA. Returns the set value if successful.
            channel: 1, 2, or 3
            protection_type: "ovp" or "ocp"
            value: value in mV (for ovp) or mA (for ocp)
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if protection_type not in ["ovp", "ocp"]:
            raise ValueError("Invalid protection type. Use 'ovp' or 'ocp'.")
        
        if protection_type == "ovp":
            if channel == 3 and (value > 5500 or value < 1):
                raise ValueError("OVP for CH3 must be between 1mV and 5500 mV")
            if channel in [1, 2] and (value > 33000 or value < 1):
                raise ValueError("OVP for CH1 and CH2 must be between 1mV and 33000 mV")
        elif protection_type == "ocp":
            if value > 3300 or value < 1:
                raise ValueError("OCP must be between 1mA and 3300 mA") 

        try:
            self.inst.write(f':OUTP:{protection_type}:VAL CH{channel}, {value/1000}')
            res = self.inst.query(f':OUTP:{protection_type}:VAL? CH{channel}')
        except Exception as e:
            print(f"Error setting {protection_type} for CH{channel} to {value}: {e}")
        finally:
            if float(res) * 1000 != value:
                raise RuntimeError(f"Failed to set {protection_type} for CH{channel} to {value}: {res}")
            else:
                return float(res) # return the set value in mV/mA
        

    def protection_on(self, channel: int, protection_type: str):
        """
        Turn on overvoltage or overcurrent protection for a channel. Returns "ON" if successful.
            channel: 1, 2, or 3
            protection_type: "ovp" or "ocp"
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if protection_type not in ["ovp", "ocp"]:
            raise ValueError("Invalid protection type. Use 'ovp' or 'ocp'.")
        try:
            self.inst.write(f':OUTP:{protection_type} CH{channel}, ON')
            res = self.inst.query(f':OUTP:{protection_type}? CH{channel}')
        except Exception as e:
            print(f"Error turning on {protection_type} for CH{channel}: {e}")
        finally:
            if res != 'ON':
                raise RuntimeError(f"Failed to turn on {protection_type} for CH{channel}")
            else:
                return res # "ON"
            

    def protection_off(self, channel: int, protection_type: str):
        """
        Turn off overvoltage or overcurrent protection for a channel. Returns "OFF" if successful.
            channel: 1, 2, or 3
            protection_type: "ovp" or "ocp"
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if protection_type not in ["ovp", "ocp"]:
            raise ValueError("Invalid protection type. Use 'ovp' or 'ocp'.")
        try:
            self.inst.write(f':OUTP:{protection_type} CH{channel}, OFF')
            res = self.inst.query(f':OUTP:{protection_type}? CH{channel}')
        except Exception as e:
            print(f"Error turning off {protection_type} for CH{channel}: {e}")
        finally:
            if res != 'OFF':
                raise RuntimeError(f"Failed to turn off {protection_type} for CH{channel}")
            else:
                return res    
        

    def output_on(self, channel: int):
        """
        Turn the channel output on. Returns "ON" if successful.
            channel: 1, 2, or 3
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        try:
            self.inst.write(f':OUTP CH{channel}, ON')
            res = self.inst.query(f':OUTP? CH{channel}')
        except Exception as e:
            print(f"Error turning on output for CH{channel}: {e}")
        finally:
            if res != 'ON':
                raise RuntimeError(f"Failed to turn on output for CH{channel}")
            else:
                return res


    def output_off(self, channel: int):
        """
        Turn the channel output off. Returns "OFF" if successful.
            channel: 1, 2, or 3
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        try:
            self.inst.write(f':OUTP CH{channel}, OFF')
            res = self.inst.query(f':OUTP? CH{channel}')
        except Exception as e:
            print(f"Error turning off output for CH{channel}: {e}")
        finally:
            if res != 'OFF':
                raise RuntimeError(f"Failed to turn off output for CH{channel}")
            else:
                return res


    def get_mode(self, channel: int):
        """
        Get the mode of the channel (constant voltage or constant current). Returns "CV", "CC", or "UR".
            channel: 1, 2, or 3
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        try:
            mode = self.inst.query(f':OUTP:MODE? CH{channel}').strip()
        except Exception as e:
            print(f"Error getting mode for CH{channel}: {e}")
        else:
            return mode

    def get_measure(self, channel: int, measure_type: str):
        """
        Measure the voltage or current of a channel. Returns the measured value in mV/mA.
            channel: 1, 2, or 3
            measure_type: "voltage", "current", "ovp", or "ocp"
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if measure_type not in ["voltage", "current", "ovp", "ocp"]:
            raise ValueError("Invalid measure type. Use 'voltage', 'current', 'ovp', or 'ocp'")
        
        try:
            if measure_type == "voltage":
                res = self.inst.query(f':MEAS:VOLT? CH{channel}')
            elif measure_type == "current":
                res = self.inst.query(f':MEAS:CURR? CH{channel}')
            elif measure_type == "ovp":
                res = self.inst.query(f':OUTP:OVP:VAL? CH{channel}')
            elif measure_type == "ocp":
                res = self.inst.query(f':OUTP:OCP:VAL? CH{channel}')
        except Exception as e:
            print(f"Error measuring {measure_type} for CH{channel}: {e}")
        else:
            return float(res) * 1000 # return in mV/mA


    def query(self, command: str):
        """
        Manually send a command to the power supply. Returns the response.
            command: SCPI command string
        """
        return self.inst.query(command)
    

    def init(self):
        for ch in range(1, 4):
            self.output_off(ch)                 # turn off output
            self.set_function(ch, "voltage", 0) # set voltage to 0
            self.set_function(ch, "current", 0) # set current to 0
            self.set_protection(ch, "ovp", 1)   # set ovp to 0
            self.set_protection(ch, "ocp", 1)   # set ocp to 0
            self.protection_on(ch, "ovp")       # turn on ovp
            self.protection_on(ch, "ocp")       # turn on ocp
    