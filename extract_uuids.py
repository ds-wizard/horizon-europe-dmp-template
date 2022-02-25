from logging.config import IDENTIFIER
import pathlib
import json
import glob


def parse_vars(content: str):
    vars = dict()
    lines = content.splitlines()
    for line in lines:
        if (line.startswith('{% set') or line.startswith('{%- set')) and line.endswith('%}'):
            fragments = line.split(' ')
            name = fragments[2]
            value = fragments[4]
            if value.startswith('"') and value.endswith('"'):
                if name in vars.keys():
                    print(f'WARNING: redefined var "{name}"')
                vars[name] = value[1:-1]
    return vars


class TemplateVarChecker:

    def __init__(self, vars) -> None:
        self.vars = vars
        self.usage = {name: False for name in vars.keys()}

    def note_usage_file(self, filename: str) -> None:
        text = pathlib.Path(filename).read_text(encoding='utf-8')
        unused_vars = (k for k in self.usage.keys() if not self.usage[k])
        for name in unused_vars:
            if name in text:
                self.usage[name] = True

    def list_unused(self) -> list[str]:
        return [k for k in self.usage.keys() if not self.usage[k]]


if __name__ == '__main__':
    filename = 'src/uuids.j2'
    text = pathlib.Path(filename).read_text(encoding='utf-8')
    uuid_vars = parse_vars(text)
    #print(json.dumps(uuid_vars, indent=2))
    # checking use of vars
    checker = TemplateVarChecker(uuid_vars)
    template_files = glob.glob('./**/*.html.j2', recursive=True)
    for filename in template_files:
        checker.note_usage_file(filename)
    for name in checker.list_unused():
        print(f'WARNING: unused var "{name}"')
    pathlib.Path('uuids.json').write_text(
        data=json.dumps(uuid_vars, indent=2),
        encoding='utf-8',
    )
