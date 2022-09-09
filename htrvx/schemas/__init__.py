import os
import requests
import hashlib
from typing import Optional, Union
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
    def retrieve_xsd(file: Union[str, etree._ElementTree]) -> Optional[str]:
        ns = '{http://www.w3.org/2001/XMLSchema-instance}'
        if not isinstance(file, etree._ElementTree):
            document = etree.parse(file)
        else:
            document = file
        schemaLink = document.getroot().get(ns + 'schemaLocation')
        if schemaLink:
            for link in schemaLink.split():
                if link.endswith(".xsd"):
                    return Validator.get_schema(link)
        return None

    @staticmethod
    def get_schema(xsd_path):
        if xsd_path.startswith("http://") or xsd_path.startswith("https://"):
            new_xsd_path = f"downloaded_{hashlib.sha256(xsd_path.encode()).hexdigest()}.xsd"
            if os.path.exists(new_xsd_path):
                return new_xsd_path
            schema_req = requests.get(xsd_path)
            schema_req.raise_for_status()
            with open(new_xsd_path, "w") as f:
                f.write(schema_req.text)
            return new_xsd_path

        elif xsd_path in Schemas:
            return Schemas[xsd_path]
        return xsd_path

    def validate(self, xml_path: Union[str, etree._ElementTree]) -> bool:
        if not isinstance(xml_path, etree._ElementTree):
            xml_doc = etree.parse(xml_path)
        else:
            xml_doc = xml_path
        result = self.xmlschema.validate(xml_doc)

        return result


def simplify_log_line(string: etree._LogEntry) -> str:
    # ToDo: Add cleaning for PAGE as well ?
    return string.message.replace("{http://www.loc.gov/standards/alto/ns-v4#}", "alto:")


