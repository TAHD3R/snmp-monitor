from easysnmp import Session, SNMPVariable
from easysnmp.exceptions import EasySNMPNoSuchNameError, EasySNMPTimeoutError


class SNMPClient:
    """
    A simple Wrapper Class of EasySNMP to get the temperature and humidity of the sensor

    methods:
    - get(oid: str) -> SNMPVariable
    - get_multiple(oids: list[str]) -> list[SNMPVariable]

    properties:
    - temperature -> float | None
    - humidity -> float | None
    """

    __oid_temperature = ".1.3.6.1.4.1.37940.1.1.1.1.0"
    __oid_humidity = "1.3.6.1.4.1.37940.1.1.1.1.1"

    def __init__(self, ip: str, community: str = "public", version: int = 1, **kwargs):
        self.session: Session = Session(
            hostname=ip, community=community, version=version
        )

    def get(self, oid: str) -> SNMPVariable:
        try:
            result: SNMPVariable = self.session.get(oid)
            return result
        except EasySNMPNoSuchNameError:
            print(f"{oid} not found")
        except EasySNMPTimeoutError:
            print(f"Timeout error")

    def get_multiple(self, oids: list[str]) -> list[SNMPVariable]:
        try:
            result: list[SNMPVariable] = self.session.get(oids)
            return result
        except EasySNMPNoSuchNameError:
            print(f"{oids} not found")
        except EasySNMPTimeoutError:
            print(f"Timeout error")

    @property
    def temperature(self) -> float | None:
        try:
            _temperature = int(self.get(self.__oid_temperature).value) / 100
            return _temperature
        except AttributeError:
            return None

    @property
    def humidity(self) -> float | None:
        try:
            _humidity = int(self.get(self.__oid_humidity).value) / 100
            return _humidity
        except AttributeError:
            return None

    def __iter__(self):
        yield self.humidity
        yield self.temperature
