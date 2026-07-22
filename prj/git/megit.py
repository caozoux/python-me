#!/usr/bin/env python3
"""
Git Apply Conflict Visualizer

Visualizes git apply conflicts by:
1. First-level classification based on conflict files
2. Context mismatch: shows file and line numbers where context doesn't match (green)
3. Content conflicts: shows file and line numbers with conflict markers (red)
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


# ANSI color codes
class Colors:
    GREEN = '\033[92m'      # Context mismatch (fixable via context)
    RED = '\033[91m'        # Content conflict (needs merge resolution)
    YELLOW = '\033[93m'     # File not found
    BLUE = '\033[94m'       # Patch failed
    CYAN = '\033[96m'       # Headers
    GRAY = '\033[90m'       # Context lines
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def green(text: str) -> str:
        return f"{Colors.GREEN}{text}{Colors.RESET}"

    @staticmethod
    def red(text: str) -> str:
        return f"{Colors.RED}{text}{Colors.RESET}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

    @staticmethod
    def blue(text: str) -> str:
        return f"{Colors.BLUE}{text}{Colors.RESET}"

    @staticmethod
    def cyan(text: str) -> str:
        return f"{Colors.CYAN}{text}{Colors.RESET}"

    @staticmethod
    def gray(text: str) -> str:
        return f"{Colors.GRAY}{text}{Colors.RESET}"

    @staticmethod
    def bold(text: str) -> str:
        return f"{Colors.BOLD}{text}{Colors.RESET}"


@dataclass
class PatchHunk:
    """Represents a single hunk in a patch."""
    file_path: str
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    context_lines: List[str]
    old_lines_content: List[str]
    new_lines_content: List[str]
    old_line_numbers: List[int]  # Actual line numbers in old file for each '-' line
    new_line_numbers: List[int]  # Actual line numbers in new file for each '+' line
    hunk_number: int
    full_hunk_lines: List[str]  # Complete hunk as shown in patch (with prefixes)


@dataclass
class ConflictInfo:
    """Represents a conflict in a file."""
    file_path: str
    conflict_type: str  # 'context_mismatch' or 'content_conflict'
    line_number: int
    details: str
    context_lines: List[str] = None  # Store context for display
    patch_failed_context: List[str] = None  # Store context for patch failed

    def __post_init__(self):
        if self.context_lines is None:
            self.context_lines = []
        if self.patch_failed_context is None:
            self.patch_failed_context = []


class PatchParser:
    """Parse unified diff patch files."""

    def __init__(self, patch_content: str):
        self.patch_content = patch_content
        self.hunks: List[PatchHunk] = []

    def parse(self) -> List[PatchHunk]:
        """Parse patch and extract hunks."""
        lines = self.patch_content.split('\n')
        i = 0
        current_file = None
        hunk_count = 0

        while i < len(lines):
            line = lines[i]

            # Match file header: +++ b/path or --- a/path
            if line.startswith('+++ ') or line.startswith('--- '):
                if line.startswith('+++ '):
                    match = re.match(r'\+\+\+ b/(.+)', line)
                    if match:
                        current_file = match.group(1)

            # Match hunk header: @@ -old_start,old_lines +new_start,new_lines @@
            hunk_header = re.match(
                r'@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@',
                line
            )
            if hunk_header and current_file:
                hunk_count += 1
                old_start = int(hunk_header.group(1))
                old_lines = int(hunk_header.group(2)) if hunk_header.group(2) else 1
                new_start = int(hunk_header.group(3))
                new_lines = int(hunk_header.group(4)) if hunk_header.group(4) else 1

                # Collect hunk content and track line numbers
                i += 1
                context_lines = []
                old_lines_content = []
                new_lines_content = []
                old_line_numbers = []
                new_line_numbers = []
                full_hunk_lines = []

                # Track current position in old and new files
                current_old_line = old_start
                current_new_line = new_start

                while i < len(lines):
                    hunk_line = lines[i]
                    if i < len(lines) - 1 and (
                        lines[i + 1].startswith('diff ') or
                        lines[i + 1].startswith('+++ ') or
                        lines[i + 1].startswith('--- ') or
                        lines[i + 1].startswith('@@ ')
                    ):
                        break

                    if hunk_line == '' or hunk_line.startswith('diff '):
                        break

                    full_hunk_lines.append(hunk_line)

                    if hunk_line.startswith(' '):
                        # Context line: present in both old and new
                        context_lines.append(hunk_line[1:])
                        current_old_line += 1
                        current_new_line += 1
                    elif hunk_line.startswith('-'):
                        # Line in old file being removed
                        old_lines_content.append(hunk_line[1:])
                        old_line_numbers.append(current_old_line)
                        current_old_line += 1
                    elif hunk_line.startswith('+'):
                        # Line in new file being added
                        new_lines_content.append(hunk_line[1:])
                        new_line_numbers.append(current_new_line)
                        current_new_line += 1
                    elif hunk_line.startswith('@@'):
                        break

                    i += 1

                self.hunks.append(PatchHunk(
                    file_path=current_file,
                    old_start=old_start,
                    old_lines=old_lines,
                    new_start=new_start,
                    new_lines=new_lines,
                    context_lines=context_lines,
                    old_lines_content=old_lines_content,
                    new_lines_content=new_lines_content,
                    old_line_numbers=old_line_numbers,
                    new_line_numbers=new_line_numbers,
                    full_hunk_lines=full_hunk_lines,
                    hunk_number=hunk_count
                ))
            else:
                i += 1

        return self.hunks


class ConflictAnalyzer:
    """Analyze git apply conflicts."""

    def __init__(self, patch_path: str, repo_root: str = '.'):
        self.patch_path = Path(patch_path)
        self.repo_root = Path(repo_root)
        self.parser = None
        self.conflicts: List[ConflictInfo] = []

    def load_patch(self):
        """Load and parse the patch file."""
        with open(self.patch_path, 'r') as f:
            patch_content = f.read()
        self.parser = PatchParser(patch_content)
        self.parser.parse()

    def check_apply_dry_run(self) -> Tuple[bool, str]:
        """Run git apply --check to see if patch applies cleanly."""
        result = subprocess.run(
            ['git', 'apply', '--check', str(self.patch_path)],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stderr

    def check_apply_3way(self) -> Tuple[bool, str]:
        """Run git apply -3 to attempt 3-way merge."""
        result = subprocess.run(
            ['git', 'apply', '-3', str(self.patch_path)],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout + result.stderr

    def analyze_context_mismatch(self, hunk: PatchHunk) -> Optional[ConflictInfo]:
        """Analyze if a hunk has context mismatch.

        Check if the 3 lines before and after the hunk match in the target file.
        """
        file_path = self.repo_root / hunk.file_path

        if not file_path.exists():
            return ConflictInfo(
                file_path=hunk.file_path,
                conflict_type='file_not_found',
                line_number=0,
                details=f"File does not exist: {hunk.file_path}"
            )

        with open(file_path, 'r') as f:
            file_lines = [line.rstrip('\n') for line in f.readlines()]

        mismatch_details = []
        mismatch_line = None

        # Check if the hunk start position is valid
        if hunk.old_start > len(file_lines):
            return ConflictInfo(
                file_path=hunk.file_path,
                conflict_type='context_mismatch',
                line_number=hunk.old_start,
                details=f"Hunk starts at line {hunk.old_start} but file has only {len(file_lines)} lines"
            )

        # Build expected content from hunk (including context lines)
        # The hunk has: old_start to old_start + old_lines range
        # We need to check if the file content matches what patch expects

        # Parse the full hunk to get expected lines
        expected_lines = {}
        current_line = hunk.old_start

        for hunk_line in hunk.full_hunk_lines:
            if hunk_line.startswith(' '):
                # Context line - should match
                expected_lines[current_line] = hunk_line[1:]
                current_line += 1
            elif hunk_line.startswith('-'):
                # Removed line
                expected_lines[current_line] = hunk_line[1:]
                current_line += 1
            elif hunk_line.startswith('+'):
                # Added line - doesn't exist in old file
                pass

        # Check each line in the hunk range
        for line_num in range(hunk.old_start, hunk.old_start + hunk.old_lines):
            if line_num > len(file_lines):
                break

            actual = file_lines[line_num - 1]  # Convert to 0-indexed
            expected = expected_lines.get(line_num)

            if expected is not None and expected != actual:
                mismatch_line = line_num
                mismatch_details.append(f"Line {line_num} mismatch")
                mismatch_details.append(f"  Expected: '{expected}'")
                mismatch_details.append(f"  Actual:   '{actual}'")
                break

        if mismatch_details:
            return ConflictInfo(
                file_path=hunk.file_path,
                conflict_type='context_mismatch',
                line_number=mismatch_line or hunk.old_start,
                details='\n'.join(mismatch_details)
            )

        return None

    def analyze_conflicts(self):
        """Main analysis function."""
        self.load_patch()

        # First, try a simple check to detect basic failures
        check_success, check_output = self.check_apply_dry_run()

        self.conflicts = []
        files_with_content_conflicts = set()
        files_with_basic_failures = set()

        # Parse basic failures from --check output
        check_failed_matches = re.finditer(r"error: patch failed: (.+):(\d+)", check_output)
        for match in check_failed_matches:
            file_path = match.group(1)
            line_num = int(match.group(2))
            files_with_basic_failures.add(file_path)
            self.conflicts.append(ConflictInfo(
                file_path=file_path,
                conflict_type='patch_failed',
                line_number=line_num,
                details=f"Basic patch check failed at line {line_num}"
            ))

        if check_success:
            print("✓ Patch applies cleanly!")
            return

        # Save current state BEFORE running git apply -3
        self._save_state()

        # Now try 3-way merge to detect content conflicts
        merge_success, merge_output = self.check_apply_3way()

        # Check for "Applied patch to 'file' with conflicts"
        conflict_match = re.search(r"Applied patch to '(.+)' with conflicts", merge_output)
        if conflict_match:
            conflicted_file = conflict_match.group(1)
            files_with_content_conflicts.add(conflicted_file)
            self._analyze_conflict_markers(conflicted_file)

        # Also check for any files with conflict markers
        for hunk in self.parser.hunks:
            if hunk.file_path not in files_with_content_conflicts:
                if self._check_and_add_conflict_markers(hunk.file_path):
                    files_with_content_conflicts.add(hunk.file_path)

        # Note: We DON'T restore here - let the caller decide based on --no-restore flag

        # For hunks without conflicts yet, check for context mismatch
        # We need to restore temporarily to check context mismatch
        temp_state = {}
        if hasattr(self, '_saved_files'):
            # Save current (possibly modified) state
            for file_path in self._saved_files.keys():
                full_path = self.repo_root / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        temp_state[file_path] = f.read()

            # Restore to analyze context mismatch
            self.restore_state()

            # Collect patch_failed context while file is in original state
            for conflict in self.conflicts:
                if conflict.conflict_type == 'patch_failed':
                    # Find the hunk for this file and analyze context mismatch
                    for hunk in self.parser.hunks:
                        if hunk.file_path == conflict.file_path:
                            mismatch = self.analyze_context_mismatch(hunk)
                            if mismatch and mismatch.details:
                                # Append details to existing conflict
                                conflict.details += f"\n{mismatch.details}"
                            # Save context for display
                            conflict.patch_failed_context = self._get_patch_failed_context_lines(
                                conflict.file_path, conflict.line_number
                            )
                            break

        for hunk in self.parser.hunks:
            if hunk.file_path not in files_with_content_conflicts:
                conflict = self.analyze_context_mismatch(hunk)
                if conflict:
                    # Avoid duplicates
                    if not any(
                        c.file_path == hunk.file_path and
                        c.line_number == conflict.line_number
                        for c in self.conflicts
                    ):
                        self.conflicts.append(conflict)

        # Restore back to the state with conflict markers (if any)
        if hasattr(self, '_saved_files') and temp_state:
            for file_path, content in temp_state.items():
                full_path = self.repo_root / file_path
                with open(full_path, 'w') as f:
                    f.write(content)

    def _save_state(self):
        """Save current state of files that might be modified."""
        self._saved_files = {}
        for hunk in self.parser.hunks:
            file_path = self.repo_root / hunk.file_path
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self._saved_files[hunk.file_path] = f.read()

    def restore_state(self):
        """Restore saved file state."""
        if not hasattr(self, '_saved_files'):
            return
        for file_path, content in self._saved_files.items():
            full_path = self.repo_root / file_path
            with open(full_path, 'w') as f:
                f.write(content)

    def _analyze_conflict_markers(self, file_path: str):
        """Analyze conflict markers in a file."""
        full_path = self.repo_root / file_path

        if not full_path.exists():
            return

        with open(full_path, 'r') as f:
            lines = f.readlines()

        in_conflict = False
        conflict_start = 0

        for i, line in enumerate(lines, 1):
            if '<<<<<<<' in line:
                in_conflict = True
                conflict_start = i
            elif '>>>>>>>' in line and in_conflict:
                in_conflict = False
                # Save context lines for display
                context_start = max(0, conflict_start - 4)
                context_end = min(len(lines), i + 3)
                context = [f"{j+1:4d}: {lines[j].rstrip('\n')}" for j in range(context_start, context_end)]
                self.conflicts.append(ConflictInfo(
                    file_path=file_path,
                    conflict_type='content_conflict',
                    line_number=conflict_start,
                    details=f"Content conflict from line {conflict_start} to {i}",
                    context_lines=context
                ))

    def _check_and_add_conflict_markers(self, file_path: str) -> bool:
        """Check if file has conflict markers and add to conflicts list.

        Returns True if conflict markers were found.
        """
        full_path = self.repo_root / file_path

        if not full_path.exists():
            return False

        with open(full_path, 'r') as f:
            content = f.read()

        if '<<<<<<<' in content:
            self._analyze_conflict_markers(file_path)
            return True
        return False

    def print_report(self):
        """Print a formatted conflict report."""
        if not self.conflicts:
            print(Colors.green("✓ No conflicts detected!"))
            return

        # First-level classification by file
        by_file = defaultdict(list)
        for conflict in self.conflicts:
            by_file[conflict.file_path].append(conflict)

        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}Git Apply Conflict Report{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

        for file_path, conflicts in sorted(by_file.items()):
            print(f"📄 {Colors.bold(file_path)}")
            print(f"   {Colors.gray('─'*56)}")

            for conflict in conflicts:
                icon = {
                    'context_mismatch': '🔍',
                    'content_conflict': '⚔️',
                    'patch_failed': '❌',
                    'file_not_found': '📁',
                }.get(conflict.conflict_type, '❓')

                type_name = {
                    'context_mismatch': 'Context Mismatch',
                    'content_conflict': 'Content Conflict',
                    'patch_failed': 'Patch Failed',
                    'file_not_found': 'File Not Found',
                }.get(conflict.conflict_type, conflict.conflict_type)

                # Color based on conflict type
                if conflict.conflict_type == 'context_mismatch':
                    colored_type = Colors.green(type_name)
                elif conflict.conflict_type == 'content_conflict':
                    colored_type = Colors.red(type_name)
                elif conflict.conflict_type == 'patch_failed':
                    colored_type = Colors.blue(type_name)
                elif conflict.conflict_type == 'file_not_found':
                    colored_type = Colors.yellow(type_name)
                else:
                    colored_type = type_name

                print(f"\n   {icon} {colored_type} @ line {conflict.line_number}")
                for detail_line in conflict.details.split('\n'):
                    if detail_line.strip():
                        print(f"      {detail_line}")

                # Show context for content conflicts (RED)
                if conflict.conflict_type == 'content_conflict':
                    self._show_conflict_context(file_path, conflict.line_number, conflict.context_lines, Colors.RED)
                # Show detailed comparison for context mismatch (GREEN)
                elif conflict.conflict_type == 'context_mismatch':
                    self._show_context_mismatch_details(file_path, conflict, Colors.GREEN)
                # For patch_failed, also show context mismatch details (GREEN)
                elif conflict.conflict_type == 'patch_failed':
                    self._show_patch_failed_context(file_path, conflict.line_number, Colors.GREEN, conflict.patch_failed_context)

            print()

    def _show_context_mismatch_details(self, file_path: str, conflict: ConflictInfo, color: str = Colors.GREEN):
        """Show detailed comparison for context mismatch."""
        # Find the hunk related to this conflict
        matching_hunk = None
        for hunk in self.parser.hunks:
            if hunk.file_path == file_path and hunk.old_line_numbers:
                if conflict.line_number in hunk.old_line_numbers or \
                   any(abs(conflict.line_number - n) <= 3 for n in hunk.old_line_numbers):
                    matching_hunk = hunk
                    break

        if not matching_hunk:
            return

        full_path = self.repo_root / file_path
        if not full_path.exists():
            return

        with open(full_path, 'r') as f:
            file_lines = [line.rstrip('\n') for line in f.readlines()]

        # Show 3 lines before and after the conflict
        show_lines = 3
        start = max(0, conflict.line_number - show_lines - 1)
        end = min(len(file_lines), conflict.line_number + show_lines)

        print(f"      {color}Patch expected vs actual:{Colors.RESET}")

        for i in range(start, end):
            line_num = i + 1
            actual_line = file_lines[i]

            # Find what the patch expects at this line
            expected_line = None

            # Check if this line is in the hunk's old lines
            if line_num in matching_hunk.old_line_numbers:
                idx = matching_hunk.old_line_numbers.index(line_num)
                expected_line = matching_hunk.old_lines_content[idx]

            # Check if this line is in the hunk's new lines
            elif line_num in matching_hunk.new_line_numbers:
                idx = matching_hunk.new_line_numbers.index(line_num)
                expected_line = matching_hunk.new_lines_content[idx]

            # Display the comparison
            prefix = "    "
            if line_num == conflict.line_number:
                prefix = "►  "

            if expected_line is not None and expected_line != actual_line:
                print(f"      {prefix}Line {line_num:4d}:")
                print(f"           {color}Expected: '{expected_line}'{Colors.RESET}")
                print(f"           {color}Actual:   '{actual_line}'{Colors.RESET}")
            else:
                print(f"      {prefix}Line {line_num:4d}: '{actual_line}'")

    def _show_conflict_context(self, file_path: str, line_number: int, context_lines: List[str] = None, color: str = Colors.RED):
        """Show lines around a conflict for context."""
        if context_lines:
            # Use saved context
            print(f"      {color}Context:{Colors.RESET}")
            for ctx_line in context_lines:
                parts = ctx_line.split(':', 1)
                if len(parts) == 2:
                    num, content = parts
                    num = int(num.strip())
                    content = content.strip()
                    prefix = "  │ "
                    if num == line_number:
                        prefix = "► │"
                    elif '<<<<<<<' in content or '>>>>>>>' in content or '=======' in content:
                        prefix = "▌ │"

                    # Color the conflict markers and content
                    if '<<<<<<<' in content or '>>>>>>>' in content or '=======' in content:
                        content = f"{color}{content}{Colors.RESET}"
                    elif num == line_number:
                        content = f"{color}{content}{Colors.RESET}"

                    print(f"      {prefix} {num:4d}: {content}")
                else:
                    print(f"      {ctx_line}")
            return

        # Fallback: read from file
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return

        with open(full_path, 'r') as f:
            lines = f.readlines()

        # Show 3 lines before and after
        start = max(0, line_number - 4)
        end = min(len(lines), line_number + 3)

        print(f"      {color}Context:{Colors.RESET}")
        for i in range(start, end):
            line = lines[i].rstrip('\n')
            prefix = "  │ "
            if i + 1 == line_number:
                prefix = "► │"
            elif '<<<<<<<' in line or '>>>>>>>' in line or '=======' in line:
                prefix = "▌ │"

            # Color conflict markers
            if '<<<<<<<' in line or '>>>>>>>' in line or '=======' in line:
                line = f"{color}{line}{Colors.RESET}"
            elif i + 1 == line_number:
                line = f"{color}{line}{Colors.RESET}"

            print(f"      {prefix} {i+1:4d}: {line}")

    def _show_patch_failed_context(self, file_path: str, line_number: int, color: str = Colors.GREEN, saved_context: List[str] = None):
        """Show context for patch failed scenarios."""
        print(f"      {color}File context at failure point:{Colors.RESET}")

        if saved_context:
            # Use saved context
            for line in saved_context:
                print(f"      {color}{line}{Colors.RESET}")
            return

        # Fallback: read from file
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return

        with open(full_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]

        # Find the hunk for this file
        matching_hunk = None
        for hunk in self.parser.hunks:
            if hunk.file_path == file_path:
                matching_hunk = hunk
                break

        if not matching_hunk:
            return

        # Show 3 lines before and after the reported line
        show_lines = 3
        start = max(0, line_number - show_lines - 1)
        end = min(len(lines), line_number + show_lines)

        for i in range(start, end):
            line_num = i + 1
            actual_line = lines[i]

            prefix = "    │"
            if line_num == line_number:
                prefix = "►  │"

            # Find what the patch expects at this line
            expected_line = None
            if matching_hunk.old_line_numbers and line_num in matching_hunk.old_line_numbers:
                idx = matching_hunk.old_line_numbers.index(line_num)
                expected_line = matching_hunk.old_lines_content[idx]

            if expected_line is not None and expected_line != actual_line:
                print(f"      {prefix} Line {line_num:4d}: {color}'{actual_line}'{Colors.RESET}")
                print(f"           {color}(expected: '{expected_line}'){Colors.RESET}")
            else:
                print(f"      {prefix} Line {line_num:4d}: '{actual_line}'")

    def _get_patch_failed_context_lines(self, file_path: str, line_number: int) -> List[str]:
        """Get context lines for patch failed scenario (to be displayed later)."""
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return []

        with open(full_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]

        # Find the hunk for this file
        matching_hunk = None
        for hunk in self.parser.hunks:
            if hunk.file_path == file_path:
                matching_hunk = hunk
                break

        if not matching_hunk:
            return []

        # Show 3 lines before and after the reported line
        show_lines = 3
        start = max(0, line_number - show_lines - 1)
        end = min(len(lines), line_number + show_lines)

        context_info = []

        for i in range(start, end):
            line_num = i + 1
            actual_line = lines[i]

            # Find what the patch expects at this line
            expected_line = None
            if matching_hunk.old_line_numbers and line_num in matching_hunk.old_line_numbers:
                idx = matching_hunk.old_line_numbers.index(line_num)
                expected_line = matching_hunk.old_lines_content[idx]

            marker = "    │"
            if line_num == line_number:
                marker = "►  │"

            if expected_line is not None and expected_line != actual_line:
                context_info.append(f"{marker} Line {line_num:4d}: '{actual_line}'")
                context_info.append(f"         (expected: '{expected_line}')")
            else:
                context_info.append(f"{marker} Line {line_num:4d}: '{actual_line}'")

        return context_info


def main():
    parser = argparse.ArgumentParser(
        description='Visualize git apply conflicts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my.patch                # Analyze conflicts in my.patch
  %(prog)s my.patch --repo /path/to/repo  # Analyze in specific repo
  %(prog)s my.patch --verbose      # Show detailed output
        """
    )
    parser.add_argument('patch_file', help='Path to the patch file')
    parser.add_argument(
        '--repo', '-r',
        default='.',
        help='Path to git repository (default: current directory)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean up .rej files after analysis'
    )
    parser.add_argument(
        '--no-restore',
        action='store_true',
        help='Do not restore file state after analysis (leaves conflict markers)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.patch_file):
        print(f"Error: Patch file not found: {args.patch_file}", file=sys.stderr)
        return 1

    analyzer = ConflictAnalyzer(args.patch_file, args.repo)

    try:
        analyzer.analyze_conflicts()
        analyzer.print_report()

        if not args.no_restore:
            # Restore original file state
            analyzer.restore_state()

        if args.clean:
            # Clean up .rej and .orig files
            subprocess.run(
                ['find', str(analyzer.repo_root), '-name', '*.rej', '-delete'],
                capture_output=True
            )
            subprocess.run(
                ['find', str(analyzer.repo_root), '-name', '*.orig', '-delete'],
                capture_output=True
            )

        return 0 if not analyzer.conflicts else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if not args.no_restore:
            analyzer.restore_state()
        return 1


if __name__ == '__main__':
    sys.exit(main())
