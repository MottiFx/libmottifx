from procmottifx.systems.protos import schema_pb2 as sch


class AudioSfx:
    def __init__(self,aud=None,prog=None):
        """
            "volume": 1.0
        """
        self.aud = aud

        if prog:
            data = {prg.name: prg.value for prg in prog}
            if "volume" in data:
                self.aud *= float(data["volume"])

    def render(self):
        return self.aud
                
    def add_data(self):
        data = [
            {"key": "volume","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"volume","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"2."}
        ]
        return data
