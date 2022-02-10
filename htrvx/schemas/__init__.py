import os
import requests
from lxml import etree

_here = os.path.dirname(__file__)
Schemas = {
    "alto": os.path.join(_here, "", "alto4.xsd"),
    "page": os.path.join(_here, "", "page2019.xsd")
}


class Validator:
    def __init__(self, xsd_path: str):
        xmlschema_doc = etree.parse(self.get_schema(xsd_path))
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    @staticmethod
    def get_schema(xsd_path):
        if xsd_path.startswith("http://") or xsd_path.startswith("https://"):
            schema_req = requests.get(xsd_path)
            schema_req.raise_for_status()
            new_path = "downloaded.xsd"
            with open(new_path, "w") as f:
                f.write(schema_req.text)
            return new_path
        elif xsd_path in Schemas:
            return Schemas[xsd_path]
        return xsd_path

    def validate(self, xml_path: str) -> bool:
        xml_doc = etree.parse(xml_path)
        result = self.xmlschema.validate(xml_doc)

        return result


def simplify_log_line(string: etree._LogEntry) -> str:
    # ToDo: Add cleaning for PAGE as well ?
    return string.message.replace("{http://www.loc.gov/standards/alto/ns-v4#}", "alto:")


