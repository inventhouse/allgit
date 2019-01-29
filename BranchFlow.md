BranchFlow
==========
Quicker and easier branch workflow

Working on feature or bugfix branches is very common when collaborating on code in git repositories, but adhering to best-practice naming conventions like 'users/my_name/JIRA-123-my-feature' can make working with branches tedious.  The workflow gets worse if the change involves multiple repositories, and _much_ worse if we have to juggle several branches.

In fact, git lets us use different a different local vs. remote name for branches, but this feature can be arcane to use; these scripts aim to make working with well-named shared branches easier and integrate with allgit to scale across repositories.

To describe these commands and how to use them, let's call the local, shorter, name an _alias_ for the longer remote name, and let's say that the remote name is made up of a _prefix_ and a _slug_.

Assuming allgit is set up as described in [README.md](README.md), there are two more things to do, the first tells git to use the remote, "upstream", branch for push:

`$ git config --global push.default upstream`

The second sets the default branch prefix to match our shared branch naming convention:

`$ git config --global allgit.branchprefix 'users/abc'`

(This can also be overridden by setting it on particular repositories, without using `--global`, of course)

| Commands | Notes |
|----------|-------|
| _(start implementing a feature)_ ||
| `$ allgit -m -- newb JIRA-123-my-feature f` | Checks out a local branch `f` and immediately pushs it (unchanged!) to `users/abc/JIRA-123-my-feature` in all repositories with local modifications (`-m`)
| `$ allgit -b f - commit -am "WIP my feature"` | Work with the branch (`-b`) using the local alias `f`
| `$ allgit -b f - push` | Commit and push normally
| _(create PRs for branches and merge them)_ | _(( Making this easier is on the to-do list ))_ |
| `$ allgit -b f -- killb` | Check out master and delete local and remote branches

In addition to `newb` and `killb`, there are a few more commands:

- `$ allgit -- listb` will show all the branches that have a different local vs. remote name (including local-only branches)
- `$ allgit -b foo -- setupb JIRA-234-add-foobar` will push up the existing local branch `foo` (so we can separate local branch creation from pushing)
- `$ allgit -b users/abc/JIRA-112-make-a-thing -- getb t` will check out a local branch `t` for an existing remote branch
- `$ allgit -b t -- dropb` will delete the local branch t, but _not_ the remote branch


_(( describe command format - slug, alias ))_

_(( describe multiple-prefix support ))_

_(( describe use without allgit ))_


Goals
-----
- short "alias" local names, longer descriptive remote names
    - workflow should be just as easy regardless of how many repos are involved
    - easy as possible to create - programmatic prefix (maybe git-config setting?), jira tix integration? slug?
    - easy-or-automatic to avoid/deal with alias conflicts
    - easy to push/create PR  (probably need access token for that?)
    - easy to clean up
    - easy to alias-checkout remote branches


To Do
-----
- easy to list "alias" branches
    - DONE: `listb` - lists branches that don't match their upstream (including local branches)
    - allgit -a/--alias-branches? - run in repos with local branches that don't "match" upstream - needs to be a "pre-filter" in allgit though
    - should it include "pure local" branches? - probably

- `squashbranch [-c|-m message] [-p?]` - squash, re-commit with original message + squash-hashes or message + squash-hashes, force-push (pre-commit check in here somewhere?) - or maybe `squashpush` does squashbranch + extras  (Does git support precommit hook? yes, also look into https://pre-commit.com)

- Make PRs by constructing and opening github URLs:

    > remote: Create a pull request for 'bjh/thing' on GitHub by visiting:
    > remote:      https://github.com/inventhouse/Test/pull/new/bjh/thing

    - should only do this for GH-remoted repos?  What if there's a mix?  Does a GH-specific script belong in allgit?

- need an allgit utils module or something

### Doneyard

- DONE: $ALLGIT_BRANCH - mechanism for helpers that expect to be on the desired branch so they can enforce that?

- DONE: `newb` - create a local branch with short name & upstream with longer composed name
    - DONE: need `setupb SLUG` for composing upstream name after-the-fact - need to guard for already tracking?
- DONE: `killb` - clean up local and upstream branches
    - DONE: need a good way to delete just local branch but with $ALLGIT_BRANCH - `dropb`?
- DONE: `getb` - check out remote branch as alias

- DONE: how to accomodate workflows that use different branch prefixes for different types, like 'bugfix/', 'feature/'?
    - DONE: perhaps setupb should not prefix if slug contains '/'?
    - DONE: in that case, should alias extract the last part? - yes, if getb would

---
