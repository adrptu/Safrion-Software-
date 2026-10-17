"""Executa a suíte do pacote sem instalação pessoal; não usa autenticação/rede."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='skills-clean-') as isolated:
    with patch('pathlib.Path.home', return_value=Path(isolated) / 'uninstalled'):
        spec = importlib.util.spec_from_file_location('candidate_tests', root / 'test_gemini_consult.py')
        tests = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tests)
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
sys.exit(not result.wasSuccessful())
