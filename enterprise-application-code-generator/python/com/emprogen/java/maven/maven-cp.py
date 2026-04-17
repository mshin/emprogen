#!/usr/bin/env python3

#
# maven-cp.py
#
# A script to output a Java classpath for the given Maven GAVs,
# including their dependencies.
#
# Requires command line mvn to be installed.
#
# Example of usage:
#   maven-cp.py edu.ucar:netcdf:4.2.20

import sys
import os
import shutil
import subprocess

# Prefix to local Maven repository cache
HOME_DIR = os.environ.get('HOME', os.path.expanduser('~'))
REPO = os.path.join(HOME_DIR, '.m2', 'repository')

def path_prefix(gav):
    try:
        group_id, artifact_id, version = gav.split(':')
    except ValueError:
        return ""

    group_id_path = group_id.replace('.', '/')
    
    artifact_id_path = artifact_id.replace('.', '/')
    
    return os.path.join(REPO, group_id_path, artifact_id_path, version, f"{artifact_id_path}-{version}")

def process(gav_hash, gav):
    if gav in gav_hash:
        return

    prefix = path_prefix(gav)
    if not prefix:
        return
        
    gav_hash[gav] = prefix
    pom = f"{prefix}.pom"
    
    if not os.path.exists(pom):
        print(f"[WARNING] Non-existent POM: {pom}", file=sys.stderr)
        return

    result = subprocess.run(
        ['mvn', '-f', pom, 'dependency:list'], 
        capture_output=True, 
        text=True
    )
    
    in_list = False
    for line in result.stdout.splitlines():
        if "The following files have been resolved:" in line:
            in_list = True
            continue
            
        if not in_list:
            continue
            
        if ':' not in line:
            break

        clean_line = line.replace("[INFO]", "").strip()
        parts = clean_line.split(':')
        
        if len(parts) >= 5:
            group_id = parts[0]
            dep_artifact_id = parts[1]
            packaging = parts[2]
            
            version = parts[-2]
            scope = parts[-1]
            
            if packaging == 'jar' and scope in ('compile', 'runtime'):
                dep_gav = f"{group_id}:{dep_artifact_id}:{version}"
                dep_prefix = path_prefix(dep_gav)
                gav_hash[dep_gav] = dep_prefix

def main():
    if not shutil.which('mvn'):
        # Why no MVN?!?!
        sys.exit(1)

    gav_hash = {}

    for gav in sys.argv[1:]:
        process(gav_hash, gav)

    if gav_hash:
        classpath_entries = [f"{gav_hash[gav]}.jar" for gav in sorted(gav_hash.keys())]
        print(':'.join(classpath_entries))
    else:
        print()

# Because Python
if __name__ == "__main__":
    main()