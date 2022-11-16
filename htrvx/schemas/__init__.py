import os
import requests
import hashlib
from typing import Optional, Union
from lxml import etree
import logging

logger = logging.getLogger(__name__)

_here = os.path.dirname(__file__)


Schemas = {
    "alto": os.path.join(_here, "", "alto4.xsd"),
    "page": os.path.join(_here, "", "page2019.xsd")
}


class CacheResolver(etree.Resolver):
    cache = _here

    def resolve(self, URL, id, context):
        # determine cache path
        if os.path.exists(URL):
            return self.resolve_file(open(URL), context, base_url=URL)
        xsd_path = Validator.cache_xsd_path(URL)
        if os.path.exists(xsd_path):
            return self.resolve_file(open(xsd_path), context, base_url=URL)
        raise requests.HTTPError(f"Unable to reach {URL} and not found in cache at {xsd_path}")


class Validator:
    def __init__(self, xsd_path: str):
        parser = etree.XMLParser(no_network=True)
        parser.resolvers.add(CacheResolver())
        xmlschema_doc = etree.parse(self.get_schema(xsd_path), parser=parser)
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
    def cache_xsd_path(xsd_path):
        xsd_path = xsd_path.replace("http://", "").replace("https://", "")
        return os.path.join(_here, "", f"{hashlib.sha256(xsd_path.encode()).hexdigest()}.xsd")

    @staticmethod
    def get_schema(xsd_path):
        if xsd_path.startswith("http://") or xsd_path.startswith("https://"):
            new_xsd_path = f"downloaded_{hashlib.sha256(xsd_path.encode()).hexdigest()}.xsd"
            if os.path.exists(Validator.cache_xsd_path(xsd_path)):
                return Validator.cache_xsd_path(xsd_path)
            elif os.path.exists(new_xsd_path):
                return new_xsd_path
            try:
                schema_req = requests.get(xsd_path)
                schema_req.raise_for_status()
            except requests.HTTPError as E:
                logger.warning(f"HTTP error while contacting {xsd_path}: {E}. Trying HTTPS if HTTP failed.")
                # ALTO seems to throw an error because they moved to HTTP
                if xsd_path.startswith("http://"):
                    return Validator.get_schema(xsd_path.replace("http://", "https://"))
                raise
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
    return string.message.replace("{http://www.loc.gov/standards/alto/ns-v4#}", "alto:")\
        .replace("{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}", "page:")


