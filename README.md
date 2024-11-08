# Memory in the Shell

We love the `shell`. [bash](#) or [zsh](#) or [fish](#) or [powershell](#) or name
your own. But the `shell` forgets, especially when we are across multiple
systems. It would be incredible if the `shell` could *safely* remember things for us,
across systems. So let us extend the `shell` to remember things for us.

For example, here are notes from a user interview:

In my MacOS, I have all the commands I use frequently to build and compile my
projects. There are various nuances to the commands and I greatly depend on the
shell's ability to auto-complete such commands. But when I switch to
a different system, I have to either manually copy the shell history or I will
have to type all the commands at least once again. Having my shell history
synced across various machines will be helpful. It becomes even more necessary
when I am using temporary cloud VMs for testing or developing a specific
feature.

## Scope

Our interns have already worked on a part of the problem. They built an [API
for storing commands](https://github.com/safedep-hiring/swe-intern-problem-1).
But we are lost now. We need your help in analysing the full problem statement
given above, break it down into smaller tasks and write a plan of
implementation. You don't have to implement everything but we encourage you to
think as verbose as possible. Make a list of tasks including those that are
likely not required to ship a minimum viable product (MVP).

Once you have a plan of implementation, pick up the next task that you feel is
needed and do a minimum implementation for the task. Take into consideration
what has already been done by our interns and do not repeat it.

**The task that you choose must demonstrate your ability to write code for a production system.**

### Instructions

1. Feel free to use any programming language
2. Use a database if required, not just an in-memory list or map

> Note: Any database is fine. Even in-memory `sqlite`.

## Reviewer Experience

The reviewer should be able to run your application using
`docker-compose`. Additional steps are fine but should be documented.

## Submission

1. Create a [private fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of this repository.
2. Commit your code to the forked repository `dev` branch
3. Create a pull request from your `dev` branch to your `main` branch
4. Invite [@abhisek](https://github.com/abhisek) to your private fork repository
5. Add `@abhisek` as a reviewer to the pull request

## Questions?

Send email to `jobs{at-sign}safedep.io` with subject `Memory in the Shell - SWE`
