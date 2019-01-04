allgit
======
Allgit makes working with many git repositories easier, especially keeping them all up-to-date, managing branches between them, and making changes across multiple projects.

It works regardless of where the repositories came from and without requiring any configuration, maintaining lists of repositories, setting up a "super-repository", or other additional management.

It also serves as a platform for other scripts like `squashbranch`; if we can write a script that works on just one repository, allgit can run it across any number.


Example Workflow
----------------
First, have a look at `allgit -h` to see what the options mean.

| Commands                                           | Notes |
|----------------------------------------------------|-------|
|`$ allgit -cb master - pull -r`                     | Check out the master branch and pull it up-to-date in all repositories; note the `-` between the allgit options and the git command
|_(Make some changes)_                               ||
|`$ allgit -m - status`                              | Show the status of the modified repositories
|`$ allgit -m - checkout -b my_feature`              | Create a feature branch in modified repositories; we can now work with these repositories based on that branch
|`$ allgit -b my_feature - commit -am "Feature!"`    | Commit the changes
|`$ allgit -fb my_feature - rebase origin/master`    | Fetch in all repositories and rebase the feature branch from master
|`$ allgit -b my_feature -- make test`               | Run tests; note the `--` to run a non-git command
|`$ allgit -b my_feature - push -u origin my_feature`| Push the new feature up to make PRs

Note that this workflow is the same no matter how many repositories we have or even how many are involved in the feature changes - no repeating commands per repo!


More on Branches
----------------
Branches are integral to change management in git; it turns out that feature and release branches are a very natural way to group projects that allgit should work on together.  On the flip side, allgit makes it very easy make consistent branches among related projects.

In fact, it can be useful to, judiciously, make branches for the sole purpose grouping repositories; allgit's `--branches` filter just checks if the desired branches exists, they don't have to be checked out.

On the other hand, we often work with varied repositories that may branch for release on different schedules or come from multiple sources which may have differing branching and naming practices.

Allgit's `--checkout --branches` (`-cb`) was literally made for this.  By specifying a list of branches in last-one-wins order, a single command can ensure that all the projects are coherent.

For example, say we have a bunch of repositories that integrate together: some have branched for 'SpamRelease', one works from a 'development' branch, we have a feature branch across a few, and the rest should be on 'master', we could simply run:

`$ allgit -cb master SpamRelease development my_feature`

We can even add a ` - pull -r` to the end to pull them up-to-date after everything is on the right branch, as we did at the beginning of the example workflow above.


Goals
-----
- powerful and transparent
- easy to work with many repos as groups and subsets
- easy to work with branches
- good arsenal of scripts for common git tasks (_not_ built-in though)

### Non-goals
- not a "front-end", doesn't replace git nor git commands; sorry, I don't know how to fix git (yet)
- not a generalized command-runner, git-focused
- no "smarts" about the commands it runs
  - but not *too* dogmatic either: optional 'git', magic fetch, branch, and checkout options, ...
- alas, adds yet another set of hacks onto git
- not supporting old versions of Python


To Do
-----
- add bold to some of allgit output (like repo names)
  - check terminal type / capabilities?  just interactive vs. not?  cross-platform compatibility?

- clone
  - make script
    - script should handle not cloning repos that already exist
    - clone script should re-create heirarchies
    - standalone - script shouldn't depend on allgit or other things
  - auto-find github/gitlab repos for a given org/user/whatever?
    - list?
    - matching?
    - exclude?

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
    - mutually exclusive with --branches?
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

- defaults like origin and master?  other settings like default depth?
  - "magic" tags?
  - config settings?
  - env vars?
  - some combination or search path of the above?
  - helpers to set or move settings?

- pylint (and rules to make pylint reasonable)

- basic workflow example in --help
  - needs better argparse formatter

- DONE: handle bare repos
  - PUNT: some git commands don't work on bare, do we need to handle those differently? - no, no "special knowledge" of git commands
  - Need a flag for "only bare"?


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


---
