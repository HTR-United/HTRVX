import re
from typing import Dict, Optional, Union, Iterable, Tuple, List
from dataclasses import dataclass
import lxml.etree as ET

SegmontoZones = frozenset(["CustomZone",
                           "DamageZone",
                           "DecorationZone",
                           "DigitizationArtefactZone",
                           "DropCapitalZone",
                           "MainZone",
                           "MarginTextZone",
                           "MusicZone",
                           "NumberingZone",
                           "QuireMarksZone",
                           "RunningTitleZone",
                           "SealZone",
                           "StampZone",
                           "TableZone",
                           "TitlePageZone"])

SegmontoLines = frozenset(["CustomLine",
                           "DefaultLine",
                           "DropCapitalLine",
                           "InterlinearLine",
                           "MusicLine",
                           "RubricLine"])


ZoneRegex = re.compile(f"({'|'.join(SegmontoZones)})"+r"(:\w+)?(#\w+)?")
LineRegex = re.compile(f"({'|'.join(SegmontoLines)})"+r"(:\w+)?(#\w+)?")


@dataclass
class Element:
    id: str
    tagname: str
    category: Optional[str] = None
    has_content: bool = False


class XmlParser:
    def parse(self):
        raise NotImplemented

    def get_zones(self) -> Iterable[Element]:
        raise NotImplemented

    def get_textlines(self) -> Iterable[Element]:
        raise NotImplemented

    def test(self, check_empty: bool = False) -> Tuple[List[Element], List[Element], List[Element]]:
        zones_error = []
        line_error = []
        empty = []
        for zone in self.get_zones(check_empty=check_empty):
            if (zone.category and not ZoneRegex.match(zone.category)) or not zone.category:
                zones_error.append(zone)
            if not zone.has_content and check_empty:
                empty.append(zone)
        for line in self.get_textlines(check_empty=check_empty):
            if (line.category is not None and not LineRegex.match(line.category)) or line.category is None:
                line_error.append(line)
            if not line.has_content and check_empty:
                empty.append(line)
        return zones_error, line_error, empty

    def _check_line_content(self, line: ET._Element) -> bool:
        raise NotImplemented

    def _check_zone_content(self, zone: ET._Element) -> bool:
        raise NotImplemented


class PageXML(XmlParser):
    def __init__(self, file: Union[str, ET._Document]):
        if isinstance(file, str):
            self.xml = ET.parse(file)
        else:
            self.xml = file

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
        return annotations.get("structure", {}).get("type", None)

    def get_zones(self, check_empty: bool = False):
        for region in self.xml.findall(".//{*}TextRegion"):
            yield Element(
                id=region.attrib.get("id", "UnknownID"), tagname="Region",
                category=self._parse_custom(region.attrib.get("custom", "")),
                has_content=False if not check_empty else self._check_zone_content(region)
            )

    def _check_zone_content(self, zone: ET._Element) -> bool:
        return zone.find(".//{*}TextLine") is not None

    def get_textlines(self, check_empty: bool = False):
        for line in self.xml.findall('.//{*}TextLine'):
            yield Element(
                id=line.get("ID", "UnknownID"), tagname="Line",
                category=self._parse_custom(line.attrib.get("custom", "")),
                has_content=False if not check_empty else self._check_line_content(line)
            )

    def _check_line_content(self, line: ET._Element) -> bool:
        _line = line.find(".//{*}Unicode")
        if _line is not None:
            if _line.text is None:
                return False
            return bool(_line.text.strip())
        return False


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

    def get_textlines(self, check_empty: bool = False):
        for line in self.xml.findall('.//{*}TextLine'):
            yield Element(
                id=line.get("ID", "UnknownID"), tagname="Line",
                category=self._parse_tagrefs(line.get('TAGREFS', "")),
                has_content=False if not check_empty else self._check_line_content(line)
            )

    def get_zones(self, check_empty: bool = False):
        regions = []
        for x in AltoXML._Regions.keys():
            regions.extend(self.xml.findall('./{{*}}Layout/{{*}}Page/{{*}}PrintSpace/{{*}}{}'.format(x)))
        for region in regions:
            yield Element(
                id=region.get("ID", "UnknownID"), tagname="Region",
                category=self._parse_tagrefs(region.get('TAGREFS', "")),
                has_content=False if not check_empty else self._check_zone_content(region)
            )

    def _check_line_content(self, line: ET._Element) -> bool:
        _line = line.find("{*}String")
        if _line is not None:
            return bool(_line.attrib["CONTENT"].strip())
        return False

    def _check_zone_content(self, zone: ET._Element) -> bool:
        return zone.find(".//{*}TextLine") is not None
