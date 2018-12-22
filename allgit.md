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
- no "smarts" about the commands it runs
- adds yet another set of hacks onto the steaming pile that is git; sorry, I don't know how to fix git (yet)


Git Tricks
----------
- get current branch: `$ git rev-parse --abbrev-ref HEAD`  (could be useful for pushbranch/popbranch script)
- get branch point: `$ git merge-base master $(git rev-parse --abbrev-ref HEAD)`


To Do
-----
- DONE: start with git op on current repos
- DONE: specified repos
  - DONE: split args

- DONE: handle bare repos from the start
  - PUNT: some git commands don't work on bare, do we need to handle those differently? - no, no "special knowledge" of git commands
  - Need a flag for "only bare"?

- branch workflow
  - easy create, rebase, squash, push, fix, rebase, squash, push, eventually delete
  - "global" branch?

- heirarchies
  - DONE: search for repos
  - DONE: don't descend into git working repos
    - flag to search for subrepos
    - how does git cope with repos within repos?  (iirc, subrepo is simply "untracked")

- format placeholders
  - repo name
  - repo dir
  - branch
  - uuid? (never actually used that)
  - repos list? (never actually used that)

- clone
  - make script
    - clone script re-create heirarchies
  - auto-find github/gitlab repos for a given org/user/whatever?
    - list?
    - matching?
    - exclude?

### Doneyard

---
