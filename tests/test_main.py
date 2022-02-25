import os.path
from unittest import TestCase
from click.testing import CliRunner
from htrvx.cli import cmd


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
        return self._runner.invoke(cmd, ["--format", self._format, *args])

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
        self.assertIn("(1 wrongly tagged zones, 1 wrongly tagged lines)", result.output,
                      "Correct amount is found")
        self.assertIn("`WrongZoneType` tag for zones is forbidden (1 annotations): #incorrect_zone", result.output,
                      "Type is shown and zone id is shown")
        self.assertIn("`WrongLineType` tag for lines is forbidden (1 annotations): #incorrect_line", result.output,
                      "Type is shown and zone id is shown")
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_segmonto_no_tag(self):
        result = self.cmd("--verbose", "--segmonto", "--group", self.getFile("segmonto_empty_tag.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")
        self.assertIn("(1 wrongly tagged zones, 1 wrongly tagged lines)", result.output,
                      "Correct amount is found")
        self.assertIn("*Empty* tag for zones is forbidden (1 annotations): #incorrect_zone", result.output,
                      "Missing type is shown and zone id is shown")
        self.assertIn("*Empty* tag for lines is forbidden (1 annotations): #incorrect_line", result.output,
                      "Missing Type is shown and zone id is shown")
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
                "Element '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}MetadataW': "
                "This element is not expected. Expected is ( "
                "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}Metadata ). on line(s): 5",
                result.output,
                "Error is found on line 5 with details"
            )
        self.assertIn("0/1 valid XML files", result.output, "Nothing is valid")

    def test_schema_old(self):
        """ Schema should automatically be downloaded """
        result = self.cmd("--verbose", "--xsd", "--group", self.getFile("schema_old.xml"))
        self.assertEqual(result.exit_code, 0, "Test passes")

        self.assertIn("1/1 valid XML files", result.output, "Everything is valid")

    def test_combined(self):
        """ Schema should automatically be downloaded """
        result = self.cmd("--verbose", "--xsd", "--segmonto", "--group",
                          self.getFile("schema_old.xml"), self.getFile("working.xml"))
        self.assertEqual(result.exit_code, 1, "Test fails")

        self.assertIn("1/2 valid XML files", result.output, "Everything is valid")


class PageTestCase(AltoTestCase):
    FOLDER = "page"
