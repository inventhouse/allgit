allgit
======

High-Level Goals
----------------
- powerful and transparent
- easy to work with many repos as groups and subsets
- easy to work with branches
- good arsenal of scripts for common git tasks (_not_ built-in though)

### Non-goals
- not a "front-end", doesn't replace git nor git commands; sorry, I don't know how to fix git (yet)
- not a generalized command-runner, git-focused (*can* run any command, but *only* in git repos)
- no "smarts" about the commands it runs
  - but not *too* dogmatic either: optional 'git', magic fetch, branch, and checkout options, ...
- alas, adds yet another set of hacks onto git
- not supporting old versions of Python


To Do
-----
- docs
  - DONE: intro
  - DONE: example workflow
  - DONE: more on branches
  - DONE: finding and filtering
  - DONE: -c and -f
  - commands and scripts
    - other scripts in this repo
  - tricks?  (eg printing branches with -f, shell globbing for fine-tuned depth control, shell aliases for custom variants, etc)
  - perhaps extended tutorial with more concrete use-cases?
    - lift new feature branch from readme
    - more on marker branches
    - more branchflow workflows
      - "combining" separate remote branches
      - per-repo prefixes and working with such branches
  - nitty-gritty details
    - path normalization (all paths that point to the same file get normalized to the first version)
    - symlinks are not followed by find, but are by normalizer
- DONE: note about python versions, anaconda environments, and link to docs

- develop demo - add `help` target to makefiles

- more testing
  - create test assets
  - test edge-case repos: bare, local, empty, zero-commits
  - test --depth is accurate
  - test subrepos
  - symlinks? (dunno if following them is a good idea or not, but should doc either way)
  - how to unit test all this?
  - add more tests as new features are added
  - test symlinks vs. find_repos vs. --exclude vs. doing the same repo twice

- PUNT: Might be a better way to test for whether something is a repo `git rev-parse --show-toplevel` (succeeds if it's a repo) - check-for-.git heuristic is working fine, keep in case we find a counter-example
- PUNT: maybe `-m` could be faster using these: - again, this heuristic is working for now
  - succeeds if no staged changes: `git diff-index --cached --quiet --ignore-submodules HEAD --`
  - succeeds if no modified files: `git diff-files --quiet --ignore-submodules`
    - [SO reference](https://stackoverflow.com/a/5148851/12288422)

- pylint (and rules to make pylint reasonable)

- more/better error handling (catch exceptions and do something nicer with them)
  - DONE: trying to run existing script that lacks execute permission throws PermissionError
  - DONE: just catch OSError here, too many types to catch individually
- --failfast - stop-on-error
- search upward for .git so it works in subdirs the same way git does

- branch workflow
  - easy create, rebase, squash, push, fix, rebase, squash, push, eventually delete
    - maybe best done as helper scripts?
  - NO: "global" branch?
  - branchflow does some of this but not all

- zsh integration?

- `pleasemake` helper - make a target in repos where it can be easily found in the Makefile - or checkmake for use with -t?
- PUNT: use `hub` - `pushpr` helper to actually create PRs from pushed branch (or `open` the PR pages so you can add comments, reviewers, etc - linux version of `open`?)
- `githubclone` helper to mass-clone github repos - build one of these on `hub`

- DONE: `ALLGIT_GIT_TOOL` env var to swap in "alternative" git tools like hub (only change user commands; can use low-fidelity alternatives)

- `-t/--tags` - basically just like --branches but different mechanism
    - should this have a checkout mode too?
    - mutually exclusive with --branches?
- `--stashes` - like branches but for creating and applying named stashes
- `--remotes` - basically like branches, but repos that have one of those remotes

- DONE: --list - just list repositories, quoted and space-separated so you could drop them into -i/-x and get nearly full combination operations using subshell invocations
    - DONE: quoting if there are spaces - actually building compound calls requires re-parsing with sh -c to respect the quotes: ```$ sh -c "allgit -x `allgit -l | tail -1`"```; -x errors if nothing is given so add no-op junk  if inner allgit might not return anything: ```$ sh -c "allgit -x junk `ag -l -b foo|tail -1` --print-args"```
    - DONE: output a blank if there were no repos (may need to make the error message more clever)
    - DONE: print this instead of "Done" so it is predictably the last line and other output can be discarded with `| tail -1`
- -q/--quiet - suppress extra output (what about command output of various kinds?)
- --follow-symlinks - option to traverse symlinks during find_repos
- DONE: -t/--test - filter repos by an arbitrary command or script; `ag -t test -e Makefile -- make`
- PUNT: --exists - run the command if it can be found, for running scripts that some of your repos have versions of (pleasemake is a better way to do this, but requires makefile) - do this with `-t test -x script.sh`

- format placeholders
  - PUNT: repo name? - no, can be extracted from dir
  - PUNT: repo dir - to a helper, it's the current directory
  - PUNT: repo url - good for '--clone-script' workaround - did --clone-script already, can ask git for this
  - DONE: requested branch (ie last 'found branch') as $ALLGIT_BRANCH
  - uuid? (seems useful, but never actually used that)
  - PUNT: repos list? (never actually used that, maybe a "just print repos" flag/mode would be better) - not fully known
  - could some / all of these be "passed" to scripts as env vars? - might make it easier to write "subcommands"
    - sentinel var scripts could check for and print usage?

- defaults like origin and master?  other settings like default depth?
  - "magic" tags?
  - config settings?
  - env vars?
  - some combination or search path of the above?
  - helpers to set or move settings?

- basic workflow example in --help
  - needs better argparse formatter

- OtherGitUtils.md

### Doneyard

- DONE: start with git op on current repos
- DONE: specified repos
  - DONE: split args
  - DONE: allow delimiters in the command-half (requires searching for all the delimiters, split on the first, and make note of which kind)
- DONE: --version and version in help

- DONE: error handling / printing
  - DONE: error if no repos were found
  - DONE: error if all repos were filtered out

- DONE: -f/--fetch: do a fetch in all repos to ensure we have all branches and tags
- DONE: -c/--checkout?  getting awful close to actual subcommands
- PUNT: -p/--pull?  --  already have stashpull helper

- DONE: heirarchies
  - DONE: search for repos
  - DONE: -d/--depth and -r/--recursive
    - DONE: should recursive also imply "search for sub-repos"? - Yes
  - DONE: don't descend into git working repos
    - DONE: flag to search for subrepos
    - PUNT: how does git cope with repos within repos?  (iirc, subrepo is simply "untracked")
    - PUNT: what about submodules?

- PUNT: see if we can pass through git colors -- they come through inherited fds
- NO: 'parsable' output option? -- no control over underlying command output

- DONE: add bold to some of allgit output (like repo names)
  - DONE: check terminal type / capabilities - use tput, sys.stdout.isatty()
  - DONE: check for tput with shutil.which
  - DONE: test tput with `$ TERM=dumb ag - status -s`
    - `$ tput km` - has meta key, bool, true on mac, false on dumb
    - `$ tput hc` - hardcopy, bool, false on mac, false on dumb
    - blue text: `{tput('setaf', 4)}`, modes off: `{tput('sgr0')}`

- DONE: clone
  - DONE: make script
    - DONE: script should handle not cloning repos that already exist
    - DONE: clone script should re-create heirarchies
    - DONE: standalone - script shouldn't depend on allgit or other things
  - PUNT: auto-find github/gitlab repos for a given org/user/whatever?
    - list?
    - matching?
    - exclude?

- DONE: -b/--branches to select repos with those branches
  - NO: should this run other commands multiple times on repos with multiple matching branches?
  - get remote names and strip exact prefixes for branch name normalization
  - support git branch name globbing
- DONE: -m/--modified
- DONE: -i/--include - add extra repos after -b/t/m
- DONE: -x/--exclude - do not work on these repos no matter what
  - DONE: -x mustn't be fooled by foo vs. ./foo vs. foo/ vs. ../here/foo; maybe even symlinks too ...
- DONE: --dry-run - offer a way to check that -x is protecting it's repos

- DONE: handle bare repos
  - PUNT: some git commands don't work on bare, do we need to handle those differently? - no, no "special knowledge" of git commands
  - PUNT: Need a flag for "only bare"?
    - YES: maybe `*.git` is enough?


---
