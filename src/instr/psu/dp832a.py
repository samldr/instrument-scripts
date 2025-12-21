class DP832A:
    def __init__(self, rm, ip):
        self.inst = rm.open_resource(f"TCPIP::{ip}::INSTR")
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        for ch in range(1, 4):
            self.output_off(ch)
            self.set_function(ch, "voltage", 0)
            self.set_function(ch, "current", 0) 

    def about(self):
        """
        Return information about the power supply
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
        Get the status of all channels
        """
        res = {}
        for ch in range(1, 4):
            try:
                ch_status = self.inst.query(f':OUTP? CH{ch}').strip()
                voltage = self.inst.query(f':MEAS:VOLT? CH{ch}').strip()
                current = self.inst.query(f':MEAS:CURR? CH{ch}').strip()
            except Exception as e:
                print(f"Error querying status for CH{ch}: {e}")
            else:
                res[f'CH{ch}'] = {
                    'status': ch_status,
                    'voltage': voltage,
                    'current': current,
                }
        return res

    def set_function(self, channel: int, function_type: str, value: int):
        """
        Set the voltage or current limit for a channel, in mV/mA
        """
        value = value / 1000  # convert to V/A
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")

        voltage = self.inst.query(f':APPL? CH{channel}, VOLT')
        current = self.inst.query(f':APPL? CH{channel}, CURR')


        try:
            if function_type == "voltage":
                res = self.inst.query(f':APPL CH{channel},{value},{current}') 
            elif function_type == "current":
                res = self.inst.query(f':APPL CH{channel},{voltage},{value}')
            else:
                raise ValueError("Invalid function type. Use 'voltage' or 'current'.")
        except Exception as e:
            print(f"Error setting CH{channel} {function_type} to {value}: {e}")
        else:
            # format the value
            return res


    def set_protection(self, channel: int, protection_type: str, value: int):
        """
        Set the overvoltage or overcurrent protection for a channel, in mV/mA
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        if protection_type == "ovp":
            self.inst.query(f'') 
        elif protection_type == "ocp":
            self.inst.query(f'')
        else:
            raise ValueError("Invalid protection type. Use 'ovp' or 'ocp'.")
        

    def output_on(self, channel: int):
        """
        Turn the channel output on
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
        Turn the channel output off
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
        Get the mode of the channel (constant voltage or constant current)
        """
        if channel not in [1, 2, 3]:
            raise ValueError("Invalid channel")
        try:
            mode = self.inst.query(f':OUTP:MODE? CH{channel}').strip()
        except Exception as e:
            print(f"Error getting mode for CH{channel}: {e}")
        else:
            return mode


    def query(self, command: str):
        """
        Manually send a command to the power supply
        """
        return self.inst.query(command)