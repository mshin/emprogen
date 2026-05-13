import re
import com.emprogen.java.maven.functions as jmf


def fix_nested_enum_classes(java_class_files: list) -> None:
    """
    Fixes nested enum classes missing closing brackets in the given Java files.
    """
    nested_enum_classes = identify_nested_enum_classes(java_class_files)
    for nested_enum_class_file, nested_enum_class_content in nested_enum_classes.items():
        if is_nested_enum_class_missing_closing_bracket(nested_enum_class_content):
            print(
                f'Nested enum class: {nested_enum_class_file} ...is missing closing bracket.'
            )
            fixed_contents = fix_nested_enum_class(nested_enum_class_content)
            print(
                f'Adding closing bracket to end of file {nested_enum_class_file}'
            )
            with open(nested_enum_class_file, 'w') as f:
                f.write(fixed_contents)


def identify_nested_enum_classes(java_class_files: list) -> dict:
    """
    Identifies Java files containing nested enum classes.
    """
    output = {}
    for java_class_file in java_class_files:
        with open(java_class_file, 'r') as f:
            contents = f.read()
            if jmf.getInFile(
                '(?s)\npublic class .+\n\s*public enum ', java_class_file
            ):
                output[java_class_file] = contents
    return output


def fix_nested_enum_class(nested_enum_class_content: str) -> str:
    """
    Appends a closing bracket to the nested enum class content.
    In future, more changes could be added here.
    """
    return nested_enum_class_content + '\n}'


def is_nested_enum_class_missing_closing_bracket(
    nested_enum_class_content: str
) -> bool:
    """
    Checks if the nested enum class content is missing a closing bracket.
    """
    open_curly_bracket_count = len(
        re.findall(r'\{', nested_enum_class_content, re.MULTILINE)
    )
    closed_curly_bracket_count = len(
        re.findall(r'\}', nested_enum_class_content, re.MULTILINE)
    )
    return open_curly_bracket_count > closed_curly_bracket_count