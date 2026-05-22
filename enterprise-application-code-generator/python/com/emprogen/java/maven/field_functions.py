#!/usr/bin/env python3
import re


"Given the field:type and type:pkgtype dictionaries, return a field:pkgtype dict."
def map_fields_to_qualified_types(field_to_type: dict, type_to_pkg_type: dict) -> dict:
    output = field_to_type.copy()
    # for each field, get the types.
    for k, v in output.items():
        raw_types = v.replace('<', ' ').replace('>', ' ').replace(',', ' ').split(' ')
        types_set = set(raw_types)
        types_set.discard('')
        # For each type, map to the package info. 
        types_map = {}
        for t in types_set:
            # Make the type set. If it's not there, either:
            # the type doesn't require pkg or it's not in the properties file.
            if type_to_pkg_type.__contains__(t):
                types_map[t] = type_to_pkg_type[t]
        # For each type for field, replace with pkgtype.
        # Sorted to prevent replacing parts of words.
        # replacing largest words first should help.
        print('types_map: ' + str(types_map))
        for ke in sorted(types_map.keys(), key=len, reverse=True):
            #for first type in the type map, find occurances in fieldType, replace all.
            # lookahead/behind matches but doesn't include characters in match
            #(?!foo) negative lookahead (match if pattern immediately following is not foo)
            #(?<!foo) negative lookbehind (match if pattern immediately preceeding is not foo)
            #[a-zA-Z\.] match if not a character or a period.
            pattern = re.compile(r'(?<![a-zA-Z\.])(' + ke + r')(?![a-zA-Z])')
            # need to find the last item of all matches first, so replacement doesn't change indexes.
            while True:
                match_list = list(re.finditer(pattern, v))
                if not len(match_list):
                    break
                match = match_list[-1]
                # Replace the type with pkgtype
                v = v[:match.start()] + types_map[ke] + v[match.end():]
        output[k] = v
    return output


def create_field_string(field_to_pkg_type: dict, is_add_annotation_placeholder: bool) -> str:
    """
    Given the field:pkgtype dict, create field str for generated classes. 
    Alternatively, add annotation placeholder that must be replaced later.
    """
    output_str = ''
    for field, pkgtype in field_to_pkg_type.items():
        field_str = '\n    private ' + pkgtype + ' ' + field + ';\n'
        if is_add_annotation_placeholder:
            annotation_placeholder_str = '\n&%' + field + '&%'
            output_str += annotation_placeholder_str + field_str
        else:
            output_str += field_str
    return output_str

print('loaded ' + __file__)
