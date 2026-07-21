def convert_list_payload(payload_str: str) -> list[int]:
        """Converts '1,0,255' to [1, 0, 255]"""
        return [int(x) for x in payload_str.split(",") if x.strip().isdigit()]