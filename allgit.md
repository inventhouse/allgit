allgit
======
Git power-tool to rip through your repos; platform for git scripts

Goals
-----
- powerful and transparent
- easy to work with many repos as groups and subsets
- easy to work with branches
- good arsenal of scripts for common git tasks (_not_ built-in though)

### Non-goals
- not a "front-end", doesn't replace git
- not a generalized command-runner, git-focused
- no "smarts" about the commands it runs
  - but not *too* dogmatic either: optional 'git', magic format placeholders, ...
- alas, adds yet another set of hacks onto the steaming pile that is git; sorry, I don't know how to fix git (yet)


Git Tricks
----------
- get current branch: `$ git rev-parse --abbrev-ref HEAD`  (could be useful for pushbranch/popbranch script)
- get branch point: `$ git merge-base master $(git rev-parse --abbrev-ref HEAD)`


To Do
-----
- DONE: handle bare repos from the start
  - PUNT: some git commands don't work on bare, do we need to handle those differently? - no, no "special knowledge" of git commands
  - Need a flag for "only bare"?

- add bold to some of allgit output (like repo names)
- PUNT: see if we can pass through git colors -- they come through inherited fds
- NO: 'parsable' output option? -- no control over underlying command output

- branch workflow
  - easy create, rebase, squash, push, fix, rebase, squash, push, eventually delete
    - maybe best done as a helper script?
  - "global" branch?

- DONE: -b/--branches to select repos with those branches
  - NO: should this run other commands multiple times on repos with multiple matching branches?
  - get remote names and strip exact prefixes for branch name normalization
  - support git branch name globbing
- -t/--tags - basically just like --branches but different mechanism
    - should this have a checkout mode too?
- DONE: -m/--modified

- format placeholders
  - PUNT: repo name? - no, can be extracted from dir
  - repo dir
  - repo url - good for '--clone-script' workaround
  - branch? - is that current branch or specified branch?  one of each?
  - uuid? (seems useful, but never actually used that)
  - repos list? (never actually used that, maybe a "just print repos" flag/mode would be better)
  - could some / all of these be "passed" to scripts as env vars? - might make it easier to write "subcommands"
    - sentinel var scripts could check for and print usage?

- clone
  - make script
    - script should handle not cloning repos that already exist
    - clone script should re-create heirarchies
  - auto-find github/gitlab repos for a given org/user/whatever?
    - list?
    - matching?
    - exclude?

- defaults like origin and master?  other settings like default depth?
  - "magic" tags?
  - config settings?
  - env vars?
  - some combination or search path of the above?
  - helpers to set or move settings?

- pylint (and rules to make pylint reasonable)

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

---
