allgit
======
Allgit makes working with many git repositories easier, especially keeping them all up-to-date, managing branches between them, and making changes across multiple projects.

It works regardless of where the repositories came from and _without_ requiring any configuration - no lists of repositories to maintain, no "super-repository", nor any other additional management.

It also serves as a platform for other scripts - if we can write a script that works on just one repository, allgit can run it across any number.


Setup
-----
Simply `pip3 install allgit`

Aliasing `allgit` to make it as easy as possible to use is also recommended; add this to your `~/.bash_profile` or preferred shell's config file:

`alias ag='allgit'`

If you would like to use an alternative git client, for example [hub](https://hub.github.com), you can also set this environment variable:

`export ALLGIT_GIT_TOOL=hub`

Note that this tool will only be used for user-specified commands, not internally, so it does not need to be full-fidelity.


Basics and Workflow
-------------------
Allgit commands start with options that control it and how it finds and chooses repositories, a separator, and a command to run in each repo.  By default it works on all repositories immediately in the current directory, but we can filter by branches (`-b`) or locally modified (`-m`), among other things.

To separate allgit's options from the command to run, we use `--` by itself, with space on both sides; allgit will take everything that follows, as-is, to be the command it should run.  Note that the commands are run _inside_ each repository, _not_ the current directory.

Because we will often run git commands, we can use a single `-` as the separator instead and allgit will assume that what follows should be passed to git.  These are exactly equivalent: `allgit - pull` and `allgit -- git pull`.


Brief Example
-------------
| Commands                                           | Notes |
|----------------------------------------------------|-------|
|`$ allgit - pull -r`                                | Pull all repositories up-to-date; note the single `-` between allgit and the (implied-git) command
|_(Make some changes)_                               ||
|`$ allgit -m - status`                              | Show the status of the modified repositories
|`$ allgit -m - checkout -b my_feature`              | Create a feature branch in modified repositories; we can now work with these repositories based on that branch
|`$ allgit -b my_feature -- make test`               | Run tests; note the `--` to run a non-git command
|`$ allgit -b my_feature - commit -am "Feature!"`    | Commit the changes
|`$ allgit -b my_feature - push -u origin my_feature`| Push the feature branch up for collaboration or review

Note that this workflow is the same no matter how many repositories we have or even how many are involved in the feature changes - no repeating commands per repo!

(For an even better branch workflow, check out my [BranchTools](https://github.com/inventhouse/bettergit/blob/master/BranchTools.md))

_(( create a separate file with more, and more sophisticated, example workflows, also refer reader to -h/--help here ))_


More on Branches
----------------
Branches are integral to change management in git; it turns out that feature and release branches are a very natural way to group projects that allgit should work on together.  On the flip side, allgit makes it very easy make consistent branches among related projects.

_(( Does this belong as an example workflow? ))_

For example, if some of our repositories need to branch for release together, we can use an earlier release branch to create the new one; first, make sure they're all on the same branch and up-to-date:

```
$ allgit -b past_release - checkout master
$ allgit -b past_release - pull
```

Then, create the new release branch and push it up:

```
$ allgit -b past_release - checkout -b new_release
$ allgit -b past_release - push -u origin new_release
```

In fact, it can be useful to, judiciously, make branches for the sole purpose grouping repositories; allgit's `-b/--branches` filter just checks if any of the desired branches exist, they don't have to be checked out.

On the other hand, we often work with varied repositories that may branch for release on different schedules or come from multiple sources which may have differing branching and naming practices.

Allgit's `--checkout --branches` (`-cb`) was literally made for this.  By specifying a list of branches in last-one-wins order, a single command can ensure that all the projects are coherent.

For example, say we have a complex group of repositories that integrate together: we have a feature branch across a few, some have branched for 'SpamRelease', many have 'main' as their primary branch, and one still uses 'master', we could simply run:

`$ allgit -cb my_feature SpamRelease main master`

Allgit will check out the right branches in the projects that have them; we can even add a ` - pull -r` to the end to ensure they're all up-to-date.


Finding and Filtering
---------------------
Repositories grow and multiply; that's why we need allgit in the first place.  To find repositories, allgit searches one level into the directories specified on the command line (or the current directory), and doesn't search inside repositories it finds.

So, if we run it in a directory with some repositories cloned as immediate children, it will find those; if we run it while inside a repo, it will just work on the current repo.  These defaults control the scope and keep runs quick.

To search deeper, maybe we keep our repos organized in folders, we can specify those directories to search or give a`--depth` (`-d`); note it still doesn't search inside repositories unless we pass `--subrepos`.  To _really_ find them all `--recursive` (`-r`) searches to an unlimited depth and looks for subrepos.

Often, though, we want to be a bit more selective about which repos we work on.  First, we can simply give a list on the command line; while that could be tedious or error-prone, the shell's "wildcard" (or "globbing") feature can be really useful.  For example, to work only on "bare" repositories in the current directory:

`$ allgit *.git - fetch`

Allgit also offers a couple git-related filters, in addition to `--branches` covered above, `--modified` (`-m`) will select only repositories with local modifications.

We can even use commands or scripts to create our own filters with `--test` (`-t`), which takes a command and based on the exit status it will work on the repository or skip it.  For example `allgit -t test -f Makefile -- make` will use `/bin/test` to check for a Makefile and, if found, make the default target.  This must be the last allgit option and will take everything up to the separator as the test command, so that command can't have a bare `-` nor `--` (if those are necessary, we can always wrap it in a script, of course.)

These mechanisms add together, so we can readily compose a command to work on only modified repositories with certain branches among particular directories.  _(( this is awkward, trying to show that they're AND'd together ))_

Finally, for even more control, allgit offers `-i/--include` to add repos to the ones selected by the filters and `-x/--exclude` to do the opposite.


Fetch and Checkout
------------------
For the most part, allgit aims to be a transparent "dispatcher" for whatever git commands, aliases, or custom scripts we want to run; however there are a couple git operations it offers to support high-level workflows.

To ensure that we have current branches to filter on, `-f/--fetch` will do a fetch in each repository before checking branches or running commands.  This adds significant time, so it is an option; note that even without fetching, allgit always searches the remote branches our clone knows about.

The other built-in operation is `-c/--checkout`, mentioned above, which checks out branches in order of preference in repositories that have them.

Note, when testing with `--dry-run`, fetching is considered "safe" (and is necessary for showing exactly what would be done), while checkout will **not** be run, only printed.

_(( Add a section for other misc goodies like `--clone-script` ))_

---
