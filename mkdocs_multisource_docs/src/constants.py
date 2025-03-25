"""
Useful constants
"""

import os
from pathlib import Path

# main configuration
# PROJECT_ROOT = Path(__file__).parent.parent.parent
PROJECT_ROOT = Path(os.getcwd())  # user project root
TMP_FOLDER_PATH = PROJECT_ROOT / 'mt_source_tmp'  # archives processing
JAVADOC_FOLDER_PATH = PROJECT_ROOT / 'mt_source_jvd' # javadoc apidocs
BUILD_FOLDER_PATH = PROJECT_ROOT / 'mt_source_build' # after processing destination

# tests
_SRC_PATH = PROJECT_ROOT / 'mkdocs_multisource_docs'
TEST_APPLICATION_CONF = PROJECT_ROOT / 'tests' / 'assets' / 'conf.json' # only for tests
