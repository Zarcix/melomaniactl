from parsers.generics import GenericParser

class FirmwareVersion(GenericParser):
    @classmethod
    def parse(cls, payload: list[int]) -> str | list[int]:
        if not payload:
            return super().parse(payload)
        
        return ".".join(str(part) for part in payload)