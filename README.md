allgit
======
Allgit makes working with many git repositories easier, especially keeping them all up-to-date, managing branches between them, and making changes across multiple projects.

It works regardless of where the repositories came from and without requiring any configuration, maintaining lists of repositories, setting up a "super-repository", or other additional management.

It also serves as a platform for other scripts like `squashbranch`; if we can write a script that works on just one repository, allgit can run it across any number.


Setup
-----
Allgit expects to find Python 3.5+ in the path as `python3`; personally, I like the [Anaconda distribution](https://www.anaconda.com/download/) to bring macOS into the modern age.

Although allgit is self-contained other than the Python standard library, there are also some scripts to add additional functionality, so cloning this repository is recommended so it can all be kept up-to-date:

`$ git clone https://github.com/inventhouse/allgit.git`

The allgit directory can then be added to the path and the command aliased to make it as easy to use as possible; add these to your `~/.bash_profile` or preferred shell's config file:

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

For example, say we have a bunch of repositories that integrate together: some have branched for 'SpamRelease', one works from a 'development' branch, we have a feature branch across a few, and the rest should be on 'master', we could simply run:

`$ allgit -cb master SpamRelease development my_feature`

We can even add a ` - pull -r` to the end to pull them up-to-date after everything is on the right branch, as we did at the beginning of the example workflow above.


Finding and Filtering
---------------------
Repositories grow and multiply; that's why we need allgit in the first place.  To find repositories, allgit searches one level into the directories specified on the command line (or the current directory), and doesn't search inside repositories it finds.

So, if we run it in a directory with some repositories cloned as immediate children, it will find those; if we run it while inside a repo, it will just work on the current repo.  These defaults control the scope and keep runs quick.

To search deeper, maybe we keep our repos organized in folders, we can specify those directories to search or give a`--depth` (`-d`); note it still doesn't search inside repositories unless we pass `--subrepos`.  To _really_ find them all `--recursive` (`-r`) searches to an unlimited depth and looks for subrepos.

Often, though, we want to be a bit more selective about which repos we work on.  First, we can simply give a list on the command line; while that could be tedious or error-prone, the shell's "wildcard" (or "globbing") feature can be really useful.  For example, to work only on "bare" repositories in the current directory:

`$ allgit *.git - fetch`

Allgit also offers a couple git-related filters, in addition to `--branches` covered above, `--modified` (`-m`) will select only repositories with local modifications.

These three mechanisms add together, so we can readily compose a command to work on only modified repositories with certain branches among particular directories.

For even more control, allgit offers `-i/--include` to add repos to the ones selected by the filters and `-x/--exclude` to do the opposite.


Fetch and Checkout
------------------
For the most part, allgit aims to be a transparent "dispatcher" for whatever git commands, aliases, or custom scripts we want to run; however there are a couple git operations it offeres to support high-level workflows.

To ensure that we have current branches to filter on, `-f/--fetch` will do a fetch in each repository before checking branches or running commands.  This adds significant time, so it is an option; note that even without fetching, allgit always searches the remote branches your clone knows about.

The other built-in operation is `-c/--checkout`, mentioned above, which checks out branches in order of preference in repositories that have them.

Note, when testing with `--dry-run`, fetching is considered "safe" (and is necessary for showing exactly what would be done), while checkout will **not** be run, only printed.


---