from typing import Dict, Optional, Union
from dataclasses import dataclass
import lxml.etree as ET


@dataclass
class Element:
    id: str
    tagname: str
    category: Optional[str] = None


class XmlParser:
    def parse(self):
        raise NotImplemented

    def get_zones(self):
        raise NotImplemented

    def get_textlines(self):
        raise NotImplemented


class PageXML(XmlParser):
    @staticmethod
    def _parse_custom(attribute_string):
        annotations = {}
        attribute_string = attribute_string.strip()
        annotations_chunks = [l_chunk for l_chunk in attribute_string.split('}') if l_chunk.strip()]
        if annotations_chunks:
            for chunk in annotations_chunks:
                tag, vals = chunk.split('{')
                tag_vals = {}
                vals = [val.strip() for val in vals.split(';') if val.strip()]
                for val in vals:
                    key, *val = val.split(':')
                    tag_vals[key] = ":".join(val)
                annotations[tag.strip()] = tag_vals
        return annotations


class AltoXML(XmlParser):
    _Regions = {'TextBlock': 'text',
                     'IllustrationType': 'illustration',
                     'GraphicalElementType': 'graphic',
                     'ComposedBlock': 'composed'}

    def __init__(self, file: Union[str, ET._Document]):
        if isinstance(file, str):
            self.xml = ET.parse(file)
        else:
            self.xml = file
        self._classes = self._get_class_maps(self.xml)

    def _parse_tagrefs(self, attribute_string: str) -> Optional[str]:
        for tagref in attribute_string.split():
            rtype = self._classes.get(tagref, None)
            if rtype:
                return rtype
        return

    def _get_class_maps(self, doc) -> Dict[str, str]:
        cls_map = {}
        tags = doc.find('.//{*}Tags')
        if tags is not None:
            for x in ['StructureTag', 'LayoutTag', 'OtherTag']:
                for tag in tags.findall('./{{*}}{}'.format(x)):
                    cls_map[tag.get('ID')] = tag.get('LABEL')
        return cls_map

    def get_textlines(self):
        for line in self.xml.findall('.//{*}TextLine'):
            yield Element(
                id=line.get("ID", "UnknownID"), tagname="Line",
                category=self._parse_tagrefs(line.get('TAGREFS', ""))
            )

    def get_zones(self):
        regions = []
        for x in AltoXML._Regions.keys():
            regions.extend(self.xml.findall('./{{*}}Layout/{{*}}Page/{{*}}PrintSpace/{{*}}{}'.format(x)))
        for region in regions:
            yield Element(
                id=region.get("ID", "UnknownID"), tagname="Region",
                category=self._parse_tagrefs(region.get('TAGREFS', ""))
            )
