#!/usr/bin/env python3
# Copyright (c) 2018-2021 Benjamin Holt -- MIT License

"""
Lightweight tool to work with many git repositories.
"""
import argparse
import os
import os.path
from pathlib import PurePath
import re
import shutil
import subprocess as sub
import sys
#####


###  Main  ###
_name = "allgit"
_version = "1.0"

def main(args=sys.argv, env=os.environ):
    "Handle arguments, etc."
    git_tool = env.get("ALLGIT_GIT_TOOL", "git")
    mine, delim, cmd = split_args(args[1:], delims=("-", "--"))
    if cmd and delim == "-" and cmd[0] != git_tool:  # Git command must be separated by '-'...
        cmd[0:0] = [git_tool]  # ...and may omit "git" which feels redundant on the command line
    # Non-git command must be separated by '--', but doesn't get anything magically added

    usage = f"""                                                      v{_version}
    \t{_name} [DIR ...] [options] [- [{git_tool}] SUBCOMMAND]
    \t{_name} [DIR ...] [options] [-- ANY COMMAND]
    \t{_name} -h/--help"""
    description = f"""Run a {git_tool} command in all repositories in the current directory (or those specified); can also run other scripts or commands.
    """
    epilog = """Allgit makes working with many git repositories easier, especially keeping them all up-to-date, managing branches between them, and making changes across multiple projects.  Example workflow and more in the accompanying README.md or online: https://github.com/inventhouse/allgit
    """
    parser = argparse.ArgumentParser(usage=usage, description=description, epilog=epilog, add_help=False)
    dirs_group = parser.add_argument_group("Positional arguments")
    dirs_group.add_argument(
        "dirs",
        nargs="*",
        default=["."],
        metavar="DIR",
        help="Specific git repositories to work on or directories to search; defaults to the current directory.  Non-repository items are silently skipped and repositories are not searched for sub-repositories by default.",
    )

    search_group = parser.add_argument_group("Searching options")
    search_group.add_argument(
        "-d", "--depth",
        type=int,
        default=1,
        metavar="D",
        help="Depth to search for repositories; defaults to 1, meaning repositories directly sepecified or immidiately children of DIR.",
    )
    search_group.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Search for repositories to any depth; synonym for '--depth -1 --subrepos'.",
    )
    search_group.add_argument(
        "-s", "--subrepos",
        action="store_true",
        help="Search git repositories for repositories cloned as subdirectories.",
    )
    search_group.add_argument(
        "-i", "--include",
        nargs="+",
        default=[],
        metavar="DIR",
        help="Add repositories in these directories after other filters have been applied.",
    )
    search_group.add_argument(
        "-x", "--exclude",
        nargs="+",
        default=[],
        metavar="DIR",
        help="Do not work on repositories in these directories, even if they were specifically included.",
    )

    filter_group = parser.add_argument_group("Filtering options")
    filter_group.add_argument(
        "-b", "--branches",
        nargs="+",
        metavar="B",
        help="Only work on repositories which have at least one of these branches; branches should be given in first-one-wins priority order.",
    )
    filter_group.add_argument(
        "-m", "--modified",
        action="store_true",
        help="Only work on repositories with local changes (not including untracked files).",
    )
    filter_group.add_argument(
        "-t", "--test",
        nargs=argparse.REMAINDER,
        default=None,
        help="Run a command to decide if each repository should be worked on.  Note that the command is run from inside the repository, not from the current directory.  This option must be the last allgit argument and the command must not include a bare '-' nor '--' with space on both sides.",
    )

    actions_group = parser.add_argument_group("Action options")
    actions_group.add_argument(
        "-f", "--fetch",
        action="store_true",
        help="Run 'git fetch' on each repository before checking for branches or running commands.",
    )
    actions_group.add_argument(
        "-c", "--checkout",
        action="store_true",
        help="Check out the requested branches in the repositories that have them; branches should be given in first-one-wins priority order.  Has no effect if no branches are specified.",
    )
    actions_group.add_argument(
        "-l", "--list",
        action="store_true",
        help="List the repositories that were worked on at the end.",
    )
    actions_group.add_argument(
        "--clone-script",
        nargs="?",
        const=sys.stdout,
        metavar="SCRIPT.sh",
        help="Generate a bash script to reproduce this group of repositories; local repositories and branches will be noted in the script but elided.  When the script is run, existing repositories will be skipped; bare repositories will be mirrored.",
    )

    helpful_group = parser.add_argument_group("Helpful options")
    helpful_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Only run non-destructive commands and print what would have been done; repositories may be fetched, but branches will not be checked out and the sepecified command will not be run.",
    )
    helpful_group.add_argument(
        "--print-args",
        action="store_true",
        help="Print allgit arguments, command, and repositories, then exit.",
    )
    helpful_group.add_argument(
        "--version",
        action="version",
        version='%(prog)s ' + _version,
    )
    helpful_group.add_argument(
        "-h", "--help",
        action="help",
        help="Show this help message and exit.",
    )

    my_args = parser.parse_args(mine)

    if my_args.recursive:
        my_args.depth = -1
        my_args.subrepos = True

    found_repos = []
    for d in my_args.dirs:
        found_repos.extend(find_repos(d, depth=my_args.depth, subrepos=my_args.subrepos))

    include_repos = []
    for d in my_args.include:
        include_repos.extend(find_repos(d, depth=my_args.depth, subrepos=my_args.subrepos))

    exclude_repos = []
    for d in my_args.exclude:
        exclude_repos.extend(find_repos(d, depth=my_args.depth, subrepos=my_args.subrepos))

    normalize_paths(found_repos, include_repos, exclude_repos)
    repos = [ r for r in found_repos if r not in exclude_repos ]
    clean_include_repos = [ r for r in include_repos if r not in exclude_repos ]  # Keep these separate and not subject to the same filters as repos; keep original list for messaging if all repos are filtered/excluded

    if my_args.modified:
        repos = [ r for r in repos if repo_changes(r) ]

    if my_args.branches and not my_args.fetch:
        repos = [ r for r in repos if repo_branches(r, my_args.branches) ]  # Pre-filter for repos with the branches (process_repo will end up re-checking the branches, but that's pretty quick and I don't see a clean way to avoid that)

    if my_args.print_args:
        print(f"* Args:\n\t{my_args}\n* Command:\n\t{cmd}")
        print(f"* Found Repos:\n\t{found_repos}")
        if exclude_repos:
            print(f"* Excluded Repos:\n\t{exclude_repos}")
        if repos != found_repos:
            print(f"* Filtered Repos:\n\t{repos}")
        if clean_include_repos:
            print(f"* Included Repos:\n\t{clean_include_repos}")
        return 0

    if not found_repos and not clean_include_repos and not my_args.list:
        return "Error: found no repositories"
    if not repos and not clean_include_repos and not my_args.list:
        return f"Error: found {len(set(found_repos + include_repos))} repositories but all were filtered out"  # REM: error seems harsh for things like -m which might legitimately filter all repos

    xit = 0
    if cmd or my_args.clone_script or my_args.fetch or (my_args.branches and my_args.checkout) or my_args.list:  # Only call run if there's something to do
        xit = repo_loop(repos, cmd=cmd, fetch=my_args.fetch, test_cmd=my_args.test, branches=my_args.branches, checkout=my_args.checkout, dry_run=my_args.dry_run, include_repos=clean_include_repos, script_out=my_args.clone_script, print_list=my_args.list)

    if not my_args.list:
        print(f"{tput('bold')}Done.{tput('sgr0')}")
    return xit


def split_args(args, delims=("--",)):
    "Splits the argument list on the first delimiter found; returns a tuple of the first arg list, that delimiter, and the second arg list."
    indexes = { args.index(d): d for d in delims if d in args }
    if not indexes:
        return (args, None, None)

    i = min(indexes.keys())
    before = args[:i]
    after = args[i + 1:]
    return (before, indexes[i], after)


def repo_loop(repos, cmd=None, fetch=False, test_cmd=None, branches=None, checkout=False, dry_run=False, include_repos=[], script_out=None, print_list=False):
    "Run the commands in the repos, also handle clone script and errors."
    # FIXME: Somewhat better, but still twisty
    script_lines = []
    did_repos = []
    errors = {}  # {repo: [(command, error), ...], ...}
    first_print = True
    def print_header(r):
        nonlocal first_print
        if fetch or checkout or cmd:  # Only print if doing something 'interesting'; skip printing if just generating clone_script
            if not first_print:
                print("")  # Add a blank between repos if looping multiple times
            print(f"{tput('bold')}------  {r}  ------{tput('sgr0')}")
            first_print = False

    seen_repos = set()
    for r in repos:
        if r in seen_repos:
            continue  # Never do the same repo twice
        seen_repos.add(r)
        print_header(r)
        did = process_repo(r, errors, cmd=cmd, fetch=fetch, test_cmd=test_cmd, branches=branches, checkout=checkout, dry_run=dry_run)
        if did and script_out:
            script_lines.append(clone_script_line(r))
        if did and print_list:
            did_repos.append(r)

    for r in include_repos:  # FIXME: mostly duplicated code from above :-/
        if r in seen_repos:
            continue  # Never do the same repo twice
        seen_repos.add(r)
        print_header(r)
        did = process_repo(r, errors, cmd=cmd, fetch=fetch, dry_run=dry_run)  # "Included" repos are not subject to branch checks so omit branches and checkout (the latter doesn't apply if no branches are requested)
        if did and script_out:
            script_lines.append(clone_script_line(r))
        if did and print_list:
            did_repos.append(r)

    xit = 0
    if errors:
        print(f"\n{tput('bold')}ERRORS:{tput('sgr0')}", file=sys.stderr)
        for r in repos + include_repos:
            if r not in errors:
                continue
            print(f"\t{tput('bold')}{r}:{tput('sgr0')}", file=sys.stderr)
            for c, e in errors[r]:
                err = e.stderr.rstrip("\n")
                print(f"{tput('bold')}{pretty_cmd(c)}:{tput('sgr0')} {err}", file=sys.stderr)
                xit = e.returncode  # Return the last error code 'cos pick one

    if script_out and script_lines:
        script = CLONE_SCRIPT.format(repo_lines="\n".join(script_lines))
        if script_out is sys.stdout:
            if not first_print:
                print("")  # Add a blank to separate from earlier output
            print(f"{tput('bold')}Clone script:{tput('sgr0')}\n")
            first_print = False
            script_out.write(script)
            print("")  # Add a newline so main's "Done" doesn't look like part of the script
        else:
            with open(script_out, "wb") as f:
                f.write(script.encode("utf-8"))
                os.chmod(script_out, 0o755)  # FIXME: This may not work on some platforms
            print("Clone script saved as {}".format(script_out))

    if print_list:
        if not first_print:
            print("")  # Add a blank to separate from earlier output
        did_quote = [ space_quote(r) for r in did_repos ]  # Note that there are still weird parsing issues for the quotes to be respected if chaining into other commands
        print(f"{tput('bold')}Did:{tput('sgr0')}\n{' '.join(did_quote)}")  # This should be the last output if -l/--list so it can be used in other commands (and superflous output can be discarded with `| tail -1`)

    return xit


def process_repo(repo, errors, cmd=None, fetch=False, test_cmd=None, branches=None, checkout=False, dry_run=False):
    "Run commands in a repo, including optional fetch, branch-check, and checkout; also print commands when appropreate."
    # FIXME: Somewhat better, but still twisty
    print_cmd = (fetch or test_cmd or checkout)  # Print "active" commands if running more than just the user command
    if fetch:
        fetch_cmd = ["git", "fetch"]
        ok = repo_run(repo, fetch_cmd, errors=errors, print_cmd=print_cmd)
        if not ok:
            return False

    if test_cmd:
        ok = repo_run(repo, test_cmd, print_cmd=print_cmd)  # Don't collect test failures
        if not ok:
            print("Skipping")
            return False

    found_branches = None
    if branches:
        found_branches = repo_branches(repo, branches)
    if branches and not found_branches:  # REM: this won't come up if repos were pre-filtered
        print("Branches not found, skipping")
        return False
    if fetch and found_branches:  # Only print if branches might be newly-found
        print(f"Found branches: {', '.join(found_branches)}")

    if checkout and found_branches:
        checkout_cmd = ["git", "checkout", found_branches[0]]
        ok = repo_run(repo, checkout_cmd, errors=errors, print_cmd=print_cmd, dry_run=dry_run)
        if not ok:
            return False

    if cmd:
        env = None
        if found_branches:  # Make requested branch available to the command
            env = dict(os.environ)
            env["ALLGIT_BRANCH"] = found_branches[0]
        ok = repo_run(repo, cmd, env=env, errors=errors, print_cmd=print_cmd, dry_run=dry_run)
        if not ok:
            return False

    return True


def repo_run(r, cmd, env=None, errors=None, print_cmd=False, dry_run=False):
    "Runs a command and adds any error to the errors dictionary; returns True if the command was successful."
    if dry_run:
        print(pretty_cmd(cmd, prompt=f"{tput('bold')}DRY $ {tput('sgr0')}"))
        return True
    if print_cmd:
        print(pretty_cmd(cmd, prompt=f"{tput('bold')}$ {tput('sgr0')}"))
    try:
        sys.stdout.flush()
        result = sub.run(cmd, cwd=r, stderr=sub.PIPE, env=env)  # Collect stderr so it can be printed at the end
        result.stderr = result.stderr.decode("utf-8")  # Normalize stderr to string instead of bytes
    except OSError as err:  # If the command is not executable or has other issues, an error gets thrown instead of returning CP, so roll our own
        result = sub.CompletedProcess(cmd, returncode=err.errno, stderr=err.strerror)

    if result.returncode != 0:
        if errors is not None:
            if r not in errors:
                errors[r] = []
            errors[r] += [(cmd, result),]
        if result.stderr:
            print(result.stderr.rstrip("\n"), file=sys.stderr)
        return False

    return True


def normalize_paths(*file_lists):
    "Takes lists of paths and in-place normalizes names so items that point to the same file now have the same path between all the lists"
    canonical_pairs = []  # [(name, stat),...]
    def canonical_name(f):
        "Take a file and search the canonical pairs for a matching stat and return the canonical name; if not found this file and stat are added to the canonical pairs and the original file is returned"
        fs = os.stat(f)
        for cn, cs in canonical_pairs:
            if os.path.samestat(fs, cs):
                return cn
        else:
            canonical_pairs.append((f, fs))
            return f

    for l in file_lists:
        l[:] = [ canonical_name(n) for n in l ]


def pretty_cmd(c, prompt="$ "):
    "Format a command with a pseudo-prompt for display."
    return "{}{}".format(prompt, " ".join(c))


def space_quote(s):
    "Takes a string and adds quotes if it contains whitespace"
    if re.search(r"\s", s):
        return f"'{s}'"
    else:
        return s
#####


###  Repos  ###
def find_repos(root, depth=1, subrepos=False):
    "Find repos in a directory, limited to 'depth' levels."
    start_depth = len(PurePath(root).parts)
    repos = []
    for current, dirs, files in os.walk(root):  # TODO: Maybe 'in/exclude' pattern option?
        is_bare_repo = repo_is_bare(current)
        if is_bare_repo or ".git" in dirs:
            repos.append(os.path.normpath(current))
            dirs[:] = [ d for d in dirs if subrepos and not is_bare_repo and d != ".git" ]  # If searching for subrepos, don't search bare repos or .git

        current_depth = len(PurePath(current).parts)
        if depth >= 0 and current_depth - start_depth >= depth:
            dirs[:] = []  # Don't descend any deeper

    return sorted(repos)


# '* main'
# '  remotes/origin/main'
BRANCH_RE = re.compile(r"^\*?\s*(remotes/[^/]*/)?")  # Match the star-space or space-space and optional 'remotes/*/' prefix to be stripped from branch names; assumes remote names do not contain '/'  # REM: maybe we can get a list of actual remote names to work against
def repo_branches(repo, branch_list=None):
    "Returns a list of branch names for repo; remote branches are reduced to their base name (stripped of remotes/origin/) and de-duped.  If a list of desired branches is provided, only those will be returned if they exist for the repo."  # FIXME: this description is a mess
    branch_cmd = ["git", "branch", "--list", "--all",]
    if branch_list:
        branch_cmd.extend([ "*" + b for b in branch_list ])  # passing the list of branches to git pre-filters them for a small performance win, but also better debuggability; '*' wildcard matches /remotes/origin/ (and possibly other branches, but we re-filter anyway)
    result = sub.run(branch_cmd, cwd=repo, stdout=sub.PIPE, check=True)
    lines = [ s.decode("utf-8") for s in result.stdout.splitlines() ]
    branch_set = set([ BRANCH_RE.sub("", l) for l in lines ])
    if branch_list:
        return [ b for b in branch_list if b in branch_set ]  # Keep branches in the order they were requested
    else:
        return sorted(branch_set)


def repo_current_branch(repo):
    "Returns the current branch for a git repository."
    branch = None
    branch_cmd = ["git", "branch"]
    result = sub.run(branch_cmd, cwd=repo, stdout=sub.PIPE, check=True)
    lines = [ s.decode("utf-8") for s in result.stdout.splitlines() ]
    if lines:  # Empty repos don't really have branches
        current_line = [ l[2:] for l in lines if l.startswith("* ") ]
        branch = current_line[0] if current_line else None
    return branch


def repo_changes(repo, include_untracked=False):
    "Returns lines of short git status, optionally including untracked files, for repo"
    if repo_is_bare(repo):
        return []  # Git status fails in a bare repo
    status_cmd = ["git", "status", "--short"]
    if not include_untracked:
        status_cmd.append("--untracked-files=no")
    result = sub.run(status_cmd, cwd=repo, stdout=sub.PIPE, check=True)
    lines = [ s.decode("utf-8") for s in result.stdout.splitlines() ]
    return lines


def repo_remotes(repo):
    "Returns the list of remotes for a git repository."
    remote_cmd = ["git", "remote"]
    result = sub.run(remote_cmd, cwd=repo, stdout=sub.PIPE, check=True)
    lines = [ s.decode("utf-8") for s in result.stdout.splitlines() ]
    return lines


def repo_remote_url(repo, remote="origin"):
    "Returns the fetch URL for a remote for a git repository."
    remote_url_cmd = ["git", "remote", "get-url", remote]
    result = sub.run(remote_url_cmd, cwd=repo, stdout=sub.PIPE, check=True)
    lines = [ s.decode("utf-8") for s in result.stdout.splitlines() ]
    return lines[0] if lines else None


def repo_is_bare(repo):
    "Checks if a directory is a bare git repository."
    return repo.endswith(".git")  # FIXME: maybe a better heuristic? r/HEAD exists or somesuch?
#####


###  Clone  ###
CLONE_SCRIPT = """#!/bin/bash
# Auto-generated by allgit, see https://github.com/inventhouse/allgit
# When run, repositories will be cloned if they don't already exist and the working branch will be checked out; bare repos will be mirrored.
# Repositories and branches that were local to the original workareas are noted but elided.
function clone_repo {{
    if [ ! -e "$1/.git" ]; then
        git clone "$2" "$1"
        test "$3" && git -C "$1" checkout "$3"
    else
        echo "$1 exists, skipped"
    fi
}}
function clone_bare {{
    test -e "$1" && echo "$1 exists, skipped" || git clone --mirror "$2" "$1"
}}
###  Repositories  ###
{repo_lines}
#####
"""
CLONE_LINE = """{clone_func} "{repo}" "{url}" "{branch}"{comment}"""
def clone_script_line(repo):
    "Returns a line for a clone script based on details of a git repository."
    clone_func = "clone_repo"
    comment = ""
    branch = repo_current_branch(repo) or ""

    if repo_is_bare(repo):
        clone_func = "clone_bare"
        branch = ""  # Branch is ignored for bare repo clone

    remotes = repo_remotes(repo)
    if remotes:
        rem = "origin" if "origin" in remotes else remotes[0]  # FIXME: is there a better way to pick a remote if origin is missing?
        repo_url = repo_remote_url(repo, remote=rem)
        if branch:
            # Check that branch is available remotely for the script to check-out
            rem_branch_cmd = ["git", "branch", "--list", "--remotes", "{}/{}".format(rem,branch)]
            result = sub.run(rem_branch_cmd, cwd=repo, stdout=sub.PIPE, check=True)
            if not result.stdout:
                comment += "  # Local branch '{}' elided".format(branch)
                branch = ""
    else:
        clone_func = "# " + clone_func
        comment += "  # Local repo elided"
        repo_url = "file://" + os.path.abspath(repo)

    return CLONE_LINE.format(clone_func=clone_func, repo=repo, url=repo_url, branch=branch, comment=comment)
#####


###  Colors  ###
# Here's a nice tutorial on tput: http://www.linuxcommand.org/lc3_adv_tput.php
class Tput:
    "Wrapper for tput command, caches replies."
    def __init__(self):
        self.replies = {}


    def __call__(self, dummy):
        "Decorator to replace a dummy implementation with calls to tput if appropreate and available"
        if sys.stdout.isatty() and shutil.which("tput"):
            return self.lookup
        else:
            return dummy


    def lookup(self, capname, *params):
        "Get the value for a capname from tput, see man tput for more information"
        if capname not in self.replies:
            tp_cmd = ["tput", capname]
            if params:
                tp_cmd.extend([ str(p) for p in params ])
            result = sub.run(tp_cmd, stdout=sub.PIPE)
            r = ""  # Default to falsey
            if result.returncode == 0:  # If success, capability exists or property is true
                r = result.stdout.decode("utf-8") or True  # FIXME: should convert numeric replies
            self.replies[capname] = r
        return self.replies[capname]


@Tput()
def tput(capname, *params):
    "Dummy tput implementation, just returns empty string for now"
    return ""  # FIXME: this might not make much sense for some things (eg "cols"), so set up dummy replies with default values
#####


#####
if __name__ == "__main__":
    _xit = main()  # pylint: disable=invalid-name
    sys.exit(_xit)
#####
