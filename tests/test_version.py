import unittest


class TestVersionMetadata(unittest.TestCase):
    def test_version_metadata(self):
        try:
            from importlib.metadata import version, PackageNotFoundError
        except ImportError:
            from importlib_metadata import version, PackageNotFoundError  # type: ignore

        try:
            v = version("jira_agile_toolbox")
        except PackageNotFoundError:
            self.fail(
                "Could not find version metadata for 'jira_agile_toolbox'.\n"
                "This usually means the package is not installed, or the project name is incorrect.\n"
                "If you are running tests in editable mode, make sure you have run 'pip install -e .' or 'hatch run test'.\n"
                "Also, ensure you have at least one git tag if using SCM versioning."
            )
        self.assertTrue(
            isinstance(v, str) and v.strip(),
            msg="Version metadata is empty or not a string.\n" "Check your pyproject.toml and SCM versioning setup.",
        )


if __name__ == "__main__":
    unittest.main()
