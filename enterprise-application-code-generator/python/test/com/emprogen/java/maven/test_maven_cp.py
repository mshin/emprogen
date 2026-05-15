import unittest
from unittest.mock import patch, MagicMock
import com.emprogen.java.maven.maven_cp

class TestMavenCp(unittest.TestCase):
    @patch("com.emprogen.java.maven.maven_cp.print")
    @patch("com.emprogen.java.maven.maven_cp.subprocess.run")
    @patch("com.emprogen.java.maven.maven_cp.os.path.exists")
    @patch("com.emprogen.java.maven.maven_cp.shutil.which")
    @patch("com.emprogen.java.maven.maven_cp.sys")
    def test_main_with_gav(self, mock_sys, mock_which, mock_exists, mock_run, mock_print):
        # Setup mocks
        mock_sys.argv = ["com.emprogen.java.maven.maven_cp.py", "edu.ucar:netcdf:4.2.20"]
        mock_which.return_value = True
        mock_exists.return_value = True

        # Simulate mvn dependency:list output
        mock_run.return_value = MagicMock(stdout="""
[INFO] The following files have been resolved:
[INFO]    edu.ucar:netcdf:jar:4.2.20:compile
[INFO]    org.slf4j:slf4j-api:jar:1.7.25:compile
[INFO]    org.slf4j:slf4j-simple:jar:1.7.25:runtime
""")

        # Run main
        com.emprogen.java.maven.maven_cp.main()

        # Check that print was called with the expected classpath
        repo = com.emprogen.java.maven.maven_cp.REPO
        expected = [
            f"{repo}/edu/ucar/netcdf/4.2.20/netcdf-4.2.20.jar",
            f"{repo}/org/slf4j/slf4j-api/1.7.25/slf4j-api-1.7.25.jar",
            f"{repo}/org/slf4j/slf4j-simple/1.7.25/slf4j-simple-1.7.25.jar"
        ]
        expected_classpath = ":".join(sorted(expected))
        mock_print.assert_called_with(expected_classpath)

if __name__ == "__main__":
    unittest.main()