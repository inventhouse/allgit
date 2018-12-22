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

- error handling / printing

- branch workflow
  - easy create, rebase, squash, push, fix, rebase, squash, push, eventually delete
  - "global" branch?

- -b/--branches to select repos with those branches
  - checkout mode?  are those modes a good idea?
    - is this a case for a separate script? - no, no clear way to pass branch information
    - is this a case for {branch} format placeholder? - maybe, but that's a pain to type for how often it's useful
    - are there other "modes" that make sense?

- heirarchies
  - DONE: search for repos
  - DONE: -d/--depth and -r/--recursive
    - should recursive also imply "search for sub-repos"?
  - DONE: don't descend into git working repos
    - flag to search for subrepos
    - how does git cope with repos within repos?  (iirc, subrepo is simply "untracked")
    - what about submodules?

- format placeholders
  - PUNT: repo name? - no, can be extracted from dir
  - repo dir
  - repo url? - can be extracted from repo, but I used it quite a bit... (but mostly as a crutch to not learn the git way...)
  - branch?
  - uuid? (seems useful, but never actually used that)
  - repos list? (never actually used that, maybe a "just print repos" flag/mode would be better)

- clone
  - is a "clone mode" useful (or should script handle clone issues on its own?)
  - make script
    - clone script re-create heirarchies
  - auto-find github/gitlab repos for a given org/user/whatever?
    - list?
    - matching?
    - exclude?

### Doneyard

---
