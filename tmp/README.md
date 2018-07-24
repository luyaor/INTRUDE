# travis-abandonment-replication
Replication package for our MSR 2018 paper on Travis-CI abandonment, for public inspection in the interest of open science. 

# Citation
If you use this data, we would appreciate it if you cite:
~~~~
@inproceedings{widder2018abandonment,
  title={I’m Leaving You, Travis: A Continuous Integration Breakup Story},
  author={Widder, David and Hilton, Michael and K\"{a}stner, Christian and Vasilescu, Bogdan},
  booktitle={Proc.\ International Conference on Mining Software Repositories (MSR)},
  year={2018},
  organization={IEEE}
}
~~~~

# Data Description
Here is a description of the measures we refer to in the paper: 

- *lang*: the project language as determined automatically by GitHub
- *created_at*: the date of the project's first commit
- *last_build_finished_at*: the data of the project's last build (data collected circa Mar 2017)
- *first_t_commit*: the date of the first .travis.yml commit
- *last_t_commit*: the date of the last .travis.yml commit
- *active*: Whether builds are switched on
- *last_build_duration*: the duration in seconds of the last Travis build
- *yml_contribs*: the number of contributors to the .travis.yml file
- *yml_commits*: the number of commits to the .travis.yml file
- *job_count*: the number of jobs spaned by the last Travis build
- *last_build*: date of the last Travis build
- *commits*: number of project commits
- *contribs*: number of project contributors
- *last_commit*: the date of the last commit to the project
- *build_count*: the number of builds completed (data collected circa Mar 2017)
- *first_build* the date of the first Travis build
- *yml_deleted*: the date the yml file was deleted, if applicable
- *builds_period*: the number of days that builds were active on Travis
- *pushes*: the number of Push instigated builds on Travis
- *PRs*: the number of Pull Request instigated builds on Travis
- *project_age*: the age of the project in days
- *abandoned*: whether the project has abandoned Travis or not
- *commit_time_after_last_build*: the number of days between the most recent build and the most recent commit to the project
- *abandoned_and_alive"*: whether the project was still alive 30 days after the most recent build (to rule out project abandonment from Travis abandonment)
