import os.path
from unittest import TestCase
from click.testing import CliRunner
from htrvx.cli import cmd
from htrvx.testing import test_single, test
from lxml.etree import parse
import re


ansi_escape = re.compile(r'''
            \x1B  # ESC
            (?:   # 7-bit C1 Fe (except CSI)
                [@-Z\\-_]
            |     # or [ for CSI, followed by a control sequence
                \[
                [0-?]*  # Parameter bytes
                [ -/]*  # Intermediate bytes
                [@-~]   # Final byte
            )
        ''', re.VERBOSE)


class _DerivedOutput:
    def __init__(self, out):
        self.exit_code = out.exit_code
        self.output = ansi_escape.sub("", out.output)


class AltoTestCase(TestCase):
    FOLDER = "alto"
    SCHEMA_ERROR = "DescriptionW"

    def setUp(self) -> None:
        self._folder = os.path.join(
            os.path.dirname(__file__),
            "test_data",
            type(self).FOLDER
        )
        self._runner = CliRunner()
        self._format = type(self).FOLDER

    def cmd(self, *args):
        out = self._runner.invoke(cmd, ["--format", self._format, *args])
        return _DerivedOutput(out)

    def getFile(self, filename: str):
        return os.path.join(self._folder, filename)

    def test_empty_content(self):
        """ Test that the command run on Check for empty lines warns """
        result = self.cmd("--verbose", "--check-empty", self.getFile("empty_line.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes because it's only check")
        self.assertIn("Line with id #empty_line is empty", result.output,
                      "Error is found")
        self.assertIn("1/1 valid XML files", result.output, "Files do not fail on empty content")

    def test_empty_tag(self):
        """ Test that the command run on Check for empty tags warns"""
        result = self.cmd("--verbose", "--check-empty", self.getFile("empty_zone.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes because it's only check")
        self.assertIn("Region with id #empty_zone is empty", result.output,
                      "Error is found")
        self.assertIn("1/1 valid XML files", result.output, "Files do not fail on empty content")

    def test_empty_content_raise(self):
        """ Test that the command run on Check+Raise for empty lines fails """
        result = self.cmd("--verbose", "--check-empty", "--raise-empty",
                          self.getFile("empty_line.xml"))
        self.assertEqual(result.exit_code, 1, "Test fail")
        self.assertIn("Line with id #empty_line is empty", result.output,
                      "Error is found")
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_empty_tag_raise(self):
        """ Test that the command run on Check+Raise for empty tags fails """
        result = self.cmd("--verbose", "--check-empty", "--raise-empty",
                          self.getFile("empty_zone.xml"))
        self.assertEqual(result.exit_code, 1, "Test fail")
        self.assertIn("Region with id #empty_zone is empty", result.output,
                      "Error is found")
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_working(self):
        """ Test that the command run on correct files works """
        result = self.cmd("--verbose", "--check-empty", "--raise-empty", "--segmonto", "--xsd",
                          self.getFile("working.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes")
        self.assertIn("1/1 valid XML files", result.output, "Everything is valid")

    def test_segmonto_wrong_tag(self):
        result = self.cmd("--verbose", "--segmonto", "--group", self.getFile("segmonto_wrong_tag.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")
        self.assertIn("1 wrongly tagged zones", result.output, "Correct amount of zones is found")
        self.assertIn("1 wrongly tagged lines", result.output, "Correct amount of lines is found")
        self.assertIn("`WrongZoneType` tag for zone(s) is forbidden (1 annotations): #incorrect_zone", result.output,
                      "Type is shown and zone id is shown")
        self.assertIn("`WrongLineType` tag for line(s) is forbidden (1 annotations): #incorrect_line", result.output,
                      "Type is shown and zone id is shown")
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_segmonto_no_tag(self):
        result = self.cmd("--verbose", "--segmonto", "--group", self.getFile("segmonto_empty_tag.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")
        self.assertIn("1 wrongly tagged zones", result.output, "Correct amount of zones is found")
        self.assertIn("1 wrongly tagged lines", result.output, "Correct amount of lines is found")
        self.assertIn(
            "Missing tag for zone(s) is forbidden (1 annotations): #incorrect_zone", result.output,
            "Missing type is shown and zone id is shown"
        )
        self.assertIn(
            "Missing tag for line(s) is forbidden (1 annotations): #incorrect_line", result.output,
            "Missing Type is shown and zone id is shown"
        )
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_schema_fails(self):
        """ Schema should fail """
        result = self.cmd("--verbose", "--xsd", "--group", self.getFile("schema_fails.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")
        if self.FOLDER == "alto":
            self.assertIn(
                "Element 'alto:DescriptionW': This element is not expected. Expected is one of"
                " ( alto:Description, alto:Styles, alto:Tags, alto:Layout ). on line(s): 5",
                result.output,
                "Error is found on line 5 with details"
            )
        else:
            self.assertIn(
                "Element 'page:MetadataW': "
                "This element is not expected. Expected is ( "
                "page:Metadata ). on line(s): 5",
                result.output,
                "Error is found on line 5 with details"
            )
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_schema_old(self):
        """ Schema should automatically be downloaded """
        result = self.cmd("--verbose", "--xsd", "--group", self.getFile("schema_old.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes")

        self.assertIn("1/1 valid XML files", result.output, "Everything is valid")

    def test_image_no_link(self):
        """ Test should fail when no image is linked """
        result = self.cmd("--verbose", "--check-image", "--group", self.getFile("image_no_link.xml"))

        self.assertEqual(result.exit_code, 1, "Test fail")
        self.assertIn("0/1 valid XML files", result.output, "Test should fail")
        self.assertIn("Image link check's test failed: No image file were declared in the XML..",
                      result.output,
                      "Precise error should be shown for image link checking")

    def test_image_wrong_link(self):
        """ Test should fail when the linked image points nowhere"""
        result = self.cmd("--verbose", "--check-image", "--group", self.getFile("image_wronglink.xml"))
        self.assertEqual(result.exit_code, 1, "Test fail")
        self.assertIn("0/1 valid XML files", result.output, "Test should fail")

        self.assertIn("Image link check's test failed: Image file at path "
                      f"`{self.getFile('FileNotFound.jpeg')}` not found..",
                      result.output,
                      "Precise error should be shown for image link checking")

    def test_segmonto_complex(self):
        """ Schema should automatically be downloaded """
        result = self.cmd("--verbose", "--segmonto", "--group",
                          self.getFile("segmonto_complex_tags.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes")

        self.assertIn("1/1 valid XML files", result.output, "Everything is valid")

    def test_combined(self):
        """ Schema should automatically be downloaded """
        result = self.cmd("--verbose", "--xsd", "--segmonto", "--group",
                          self.getFile("schema_old.xml"), self.getFile("working.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")

        self.assertIn("1/2 valid XML files", result.output, "One file does not pass")

    def test_io_working_single(self):
        """ Schema should automatically be downloaded """
        xml = parse(self.getFile("working.xml"))
        log = test_single(
            xml, xsd=True, segmonto=True, group=True, check_empty=False,
            format=self.FOLDER
        )
        self.assertEqual(log.status, True, "Test should pass on opened files")
        self.assertEqual(len(log), 3, "Three tests should have been done")

        file = open(self.getFile("working.xml"))
        log = test_single(file, xsd=True, segmonto=True, group=True, check_empty=False,
            format=self.FOLDER)
        self.assertEqual(log.status, True, "Test should pass on opened files")
        self.assertEqual(len(log), 3, "Three tests should have been done")

    def test_io_failing_single(self):
        """ Schema should automatically be downloaded """
        xml = parse(self.getFile("empty_line.xml"))
        log = test_single(xml, xsd=True, segmonto=True, group=True, check_empty=True, raise_empty=True,
            format=self.FOLDER)
        self.assertEqual(log.status, False, "Test should pass on XML parsed files")
        self.assertEqual(len(log), 5, "Three tests should have been done")
        file = open(self.getFile("empty_line.xml"))
        log = test_single(file, xsd=True, segmonto=True, group=True, check_empty=True, raise_empty=True,
            format=self.FOLDER)
        self.assertEqual(log.status, False, "Test should pass on XML parsed files")
        self.assertEqual(len(log), 5, "Three tests should have been done")

    def test_io_working_multiple(self):
        """ Test that multiple files are checked correctly """
        xml = [
            parse(self.getFile("working.xml")),
            parse(self.getFile("working.xml"))
        ]
        log, status = test(
            xml, segmonto=True, group=True, check_empty=False,
            format=self.FOLDER
        )
        self.assertEqual(status, True, "Test should pass on opened files")
        self.assertEqual(len(log["File 001"]), 2, "Two tests should have been done")

        file = [open(self.getFile("working.xml")), open(self.getFile("working.xml"))]
        log, status = test(
            file, segmonto=True, group=True, check_empty=False,
            format=self.FOLDER
        )
        self.assertEqual(status, True, "Test should pass on opened files")
        self.assertEqual(len(log["File 001"]), 2, "Two tests should have been done")
        self.assertEqual(len(log["File 002"]), 2, "Two tests should have been done")
        for f in file:
            f.close()

    def test_io_failing_multiple(self):
        """ Test that multiple files are checked correctly """
        xml = [
            parse(self.getFile("working.xml")),
            parse(self.getFile("empty_line.xml"))
        ]
        log, status = test(
            xml, segmonto=True, group=True, check_empty=True, raise_empty=True,
            format=self.FOLDER
        )
        self.assertEqual(status, False, "Test should fail on opened files")
        self.assertEqual(len(log["File 001"]), 4, "Four tests should have been done")
        self.assertEqual(log["File 001"].status, True, "First file passes")
        self.assertEqual(len(log["File 002"]), 4, "Four tests should have been done")
        self.assertEqual(log["File 002"].status, False, "Second file fails")

        file = [open(self.getFile("working.xml")), open(self.getFile("empty_line.xml"))]
        log, status = test(
            file, segmonto=True, group=True, check_empty=True, raise_empty=True,
            format=self.FOLDER
        )
        self.assertEqual(status, False, "Test should fail on opened files")
        self.assertEqual(len(log["File 001"]), 4, "Two tests should have been done")
        self.assertEqual(log["File 001"].status, True, "First file passes")
        self.assertEqual(len(log["File 002"]), 4, "Two tests should have been done")
        self.assertEqual(log["File 002"].status, False, "Second file fails")
        for f in file:
            f.close()


class PageTestCase(AltoTestCase):
    FOLDER = "page"
