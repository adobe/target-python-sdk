#!/bin/bash

TEST_SCHEMA_DESTINATION_FOLDER=target_decisioning_engine/tests/schema

if [[ `git status --porcelain` ]]; then
  echo "Error: There are uncommitted changes.  Please commit or stash and try again."
  exit 1
fi

# preserve the current working branch name
working_folder=$(pwd)
working_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

# Add the target-sdk-testing repository as a remote, and perform the initial fetch
git remote add -f target-sdk-testing git@github.com:adobe/target-sdk-testing.git

# Create a "temp" branch based on target-sdk-testing:main
git checkout -b temp target-sdk-testing/main

# Create a synthetic "schema" branch using the commits in `/schema/` from `target-sdk-testing`
git subtree split -P schema -b schema

# Switch back to the working branch and add the new `schema` branch into `/path/to/test/schema/`.
git checkout ${working_branch}

if [ -d "$TEST_SCHEMA_DESTINATION_FOLDER" ]
then
    # the schema folder exists, merge the latest with it
    GIT_MERGE_AUTOEDIT=no git subtree merge -P ${TEST_SCHEMA_DESTINATION_FOLDER} schema --squash
else
    # the schema folder does not yet exist, add it
    git subtree add -P ${TEST_SCHEMA_DESTINATION_FOLDER} schema --squash
fi

# clean up the branches used
git branch -D schema temp

# clean up remotes
git remote rm target-sdk-testing

echo "Test Schema files in $working_folder/$TEST_SCHEMA_DESTINATION_FOLDER have been updated with the latest from target-sdk-testing."
