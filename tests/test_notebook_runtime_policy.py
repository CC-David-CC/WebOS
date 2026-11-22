from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


spec = spec_from_file_location('operator_module', Path(__file__).resolve().parents[1] / 'deploy/viewer_static_operator.py')
operator = module_from_spec(spec)
spec.loader.exec_module(operator)


class NotebookRuntimePolicy(unittest.TestCase):
    old = '/assets/desktop/apps/notebook/' + 'a' * 64
    new = '/assets/desktop/apps/notebook/' + 'b' * 64
    suffix = '/node_modules/jupyterlite/*'

    def test_rotates_only_the_two_runtime_paths(self):
        template = ('\t@other_viewer not path /wordcraft/index.html {runtime} /\n'
                    '\t@notebookRuntime path {runtime}\n'
                    '\theader @notebookRuntime >Content-Security-Policy "existing rules"\n')
        previous = template.format(runtime=self.old + self.suffix)
        updated = operator.move_notebook_policy(previous, self.old, self.new)
        self.assertEqual(updated, template.format(runtime=self.new + self.suffix))
        third = '/assets/desktop/apps/notebook/' + 'c' * 64
        self.assertEqual(operator.move_notebook_policy(updated, self.new, third), template.format(runtime=third+self.suffix))

    def test_rejects_missing_or_expanded_exception(self):
        unsafe = ('\t@other_viewer not path ' + self.old + self.suffix + '\n'
                  '\t@notebookRuntime path /assets/desktop/apps/notebook/*\n')
        with self.assertRaises(AssertionError):
            operator.move_notebook_policy(unsafe, self.old, self.new)


if __name__ == '__main__':
    unittest.main()
