allgit
======
Allgit makes working with many git repositories easier, especially keeping them all up-to-date, managing branches between them, and making changes across multiple projects.

It works regardless of where the repositories came from and without requiring any configuration, maintaining lists of repositories, setting up a "super-repository", or other additional management.

It also serves as a platform for other scripts like `squashbranch`; if we can write a script that works on just one repository, allgit can run it across any number.


Setup
-----
Allgit expects to find Python 3.5+ in the path as `python3`; personally, I like the [Anaconda distribution](https://www.anaconda.com/download/) to bring macOS into the modern age.

Although allgit is self-contained other than the Python standard libraries, cloning this repository is recommended so it can be kept up-to-date:

`$ git clone https://github.com/inventhouse/allgit.git`

It can then be added to the path and/or aliased to make it as easy to use as possible; add these to your `~/.bash_profile` or preferred shell's config file:

`PATH=$PATH:/path/to/allgit`

`alias ag='allgit'`


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

_(( Work in some of the ways we can create branches based on previous branches or collections of branches and the like ))_

In fact, it can be useful to, judiciously, make branches for the sole purpose grouping repositories; allgit's `--branches` filter just checks if any of the desired branches exist, they don't have to be checked out.

On the other hand, we often work with varied repositories that may branch for release on different schedules or come from multiple sources which may have differing branching and naming practices.

Allgit's `--checkout --branches` (`-cb`) was literally made for this.  By specifying a list of branches in last-one-wins order, a single command can ensure that all the projects are coherent.

For example, say we have a bunch of repositories that integrate together: some have branched for 'SpamRelease', one works from a 'development' branch, we have a feature branch across a few, and the rest should be on 'master', we could simply run:

`$ allgit -cb master SpamRelease development my_feature`

We can even add a ` - pull -r` to the end to pull them up-to-date after everything is on the right branch, as we did at the beginning of the example workflow above.


Finding and Filtering
---------------------
Repositories grow and multiply; that's why we need allgit in the first place.  To find repositories, allgit searches one level into the directories specified on the command line (or the current directory), and doesn't search inside repositories it finds.

So, if we run it in a directory with some repositories cloned as immediate children, it will find those; if we run it while inside a repo, it will just work on the current repo.  These defaults control the scope and keep runs quick.

To search deeper, maybe we keep our repos organized in folders, we can specify those directories to search or give a`--depth` (`-d`); note it still doesn't search inside repositories unless we pass `--subrepos`.  To _really_ find them all `--recursive` (`-r`) searches to an unlimited depth and looks for subrepos.

Often, though, we want to be a bit more selective about which repos we work on.  First, we can simply give a list on the command line, but that could be tedious or error-prone.  _(( On the other hand, work in how shell globbing can be a powerful tool ))_

Allgit offers a couple simple filters, in addition to `--branches` covered above, `--modified` (`-m`) will select only repositories with local modifications.

These three mechanisms add together, so we can readily compose a command to work on only modified repositories with certain branches among particular directories.


Goals
-----
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

- docs
  - DONE: intro
  - DONE: example workflow
  - more on branches
  - finding and filtering
  - -c and -f
  - commands and scripts
    - other scripts in this repo
  - tricks?  (eg printing branches with -f)
  - perhaps extended tutorial with more concrete use-cases?

- more testing
  - create test assets
  - test edge-case repos: bare, local, empty, zero-commits
  - test --depth is accurate
  - test subrepos
  - symlinks? (dunno if following them is a good idea or not, but should doc either way)
  - how to unit test all this?
  - add more tests as new features are added

- more/better error handling (catch exceptions and do something nicer with them)
  - DONE: trying to run existing script that lacks execute permission throws PermissionError

- branch workflow
  - easy create, rebase, squash, push, fix, rebase, squash, push, eventually delete
    - maybe best done as a helper script?
  - "global" branch?

 - `pleasemake` helper - make a target in repos where it can be easily found in the Makefile

- DONE: -b/--branches to select repos with those branches
  - NO: should this run other commands multiple times on repos with multiple matching branches?
  - get remote names and strip exact prefixes for branch name normalization
  - support git branch name globbing
- -t/--tags - basically just like --branches but different mechanism
    - should this have a checkout mode too?
    - mutually exclusive with --branches?
- DONE: -m/--modified
- -x/--exclude

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
    - maybe `*.git` is enough?


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
