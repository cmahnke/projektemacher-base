Git related notes
=================

# Fixing wrong GitHub user

Make sure the remote is configured with the right user name:

```
git remote set-url origin https://cmahnke@github.com/cmahnke/hugo-13878.git
```

# Setting the mail address for a push

```
git config user.email 194820+cmahnke@users.noreply.github.com
```

# Populating a Git Repository for GitHub error reports

```
git remote add hugo-github-issue-13878 https://github.com/jmooring/hugo-testing
git fetch hugo-github-issue-13878 hugo-github-issue-13878
git checkout -B main
git merge hugo-github-issue-13878/hugo-github-issue-13878
git push --set-upstream origin main
```
