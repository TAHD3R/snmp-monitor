from easysnmp import Session, SNMPVariable


class SNMPClient:
    __oid_temperature = ".1.3.6.1.4.1.37940.1.1.1.1.0"
    __oid_humidity = "1.3.6.1.4.1.37940.1.1.1.1.1"

    def __init__(self, ip: str, community: str = "public", version: int = 1, **kwargs):
        self.session: Session = Session(
            hostname=ip, community=community, version=version
        )

    def __iter__(self):
        yield self.humidity
        yield self.temperature

    def get(self, oid: str) -> SNMPVariable:
        result: SNMPVariable = self.session.get(oid)
        return result

    @property
    def temperature(self) -> float:
        _temperature = int(self.get(self.__oid_temperature).value) / 100
        return _temperature

    @property
    def humidity(self) -> float | None:
        _humidity = int(self.get(self.__oid_humidity).value) / 100
        return _humidity
