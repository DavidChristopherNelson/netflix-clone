import os
from pathspec import PathSpec

def main():
    root_dir = os.getcwd()
    output_file = os.path.join(root_dir, 'repository_amalgamation.txt')

    # Read and parse .gitignore
    gitignore_file = os.path.join(root_dir, '.gitignore')
    ignore_lines = []
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            ignore_lines = f.read().splitlines()

    ignore_lines.append(".git")
    ignore_lines.append("package-lock.json")
    ignore_lines.append("repository_amalgamator.py")
    spec = PathSpec.from_lines('gitwildmatch', ignore_lines)

    # Remove the existing output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Recursively collect files
    files_collected = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Calculate relative path of the current directory
        relative_dir = os.path.relpath(dirpath, root_dir)
        if relative_dir == '.':
            relative_dir = ''

        # Filter out ignored directories by mutating dirnames in-place
        dirs_to_remove = []
        for d in dirnames:
            rel_path = os.path.join(relative_dir, d) if relative_dir else d
            if spec.match_file(rel_path):
                dirs_to_remove.append(d)

        for d in dirs_to_remove:
            dirnames.remove(d)

        # Collect files that are not ignored
        for filename in filenames:
            rel_path = os.path.join(relative_dir, filename) if relative_dir else filename
            if not spec.match_file(rel_path):
                abs_path = os.path.join(dirpath, filename)
                files_collected.append(abs_path)

    # Write file paths and contents to the output file
    with open(output_file, 'w', encoding='utf-8') as out:
        for file_path in files_collected:
            rel_path = os.path.relpath(file_path, root_dir)
            # Safely read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    content = content.replace('\u2028', '\n').replace('\u2029', '\n')
            except FileNotFoundError as e:
                content = f"Failed to read file (FileNotFoundError): {e}\n"
            except PermissionError as e:
                content = f"Failed to read file (PermissionError): {e}\n"
            except UnicodeDecodeError as e:
                content = f"Failed to read file (UnicodeDecodeError): {e}\n"
            except OSError as e:
                content = f"Failed to read file (OSError): {e}\n"

            out.write(f"Path: {rel_path}\nContents:\n{content}\n\n")

    print(f"Done! Collected {len(files_collected)} files. Check {output_file}")

if __name__ == "__main__":
    main()
