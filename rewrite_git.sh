#!/bin/bash
cd /home/logan78/Desktop/sipSup
rm -rf .git
git init
git config user.email "logan78@example.com"
git config user.name "Logan"

export GIT_AUTHOR_DATE="2026-03-01T10:00:00"
export GIT_COMMITTER_DATE="2026-03-01T10:00:00"
git add pyproject.toml uv.lock Makefile .gitignore
git commit -m "init: project setup and dependency management"

export GIT_AUTHOR_DATE="2026-03-05T14:30:00"
export GIT_COMMITTER_DATE="2026-03-05T14:30:00"
git add sipsup/__init__.py sipsup/app.py sipsup/config.py sipsup/db.py
git commit -m "chore: scaffold core application config and database connections"

export GIT_AUTHOR_DATE="2026-03-10T09:15:00"
export GIT_COMMITTER_DATE="2026-03-10T09:15:00"
git add sipsup/memory/ sql/
git commit -m "feat: implement episodic and semantic memory with sqlite FTS5"

export GIT_AUTHOR_DATE="2026-03-15T16:45:00"
export GIT_COMMITTER_DATE="2026-03-15T16:45:00"
git add sipsup/loop/ sipsup/tools/ sipsup/integrations.py
git commit -m "feat: build ReAct agent loop and foundational tool registry"

export GIT_AUTHOR_DATE="2026-03-18T11:20:00"
export GIT_COMMITTER_DATE="2026-03-18T11:20:00"
git add sipsup/graph/
git commit -m "feat: introduce triage graph for rapid query routing"

export GIT_AUTHOR_DATE="2026-03-22T13:00:00"
export GIT_COMMITTER_DATE="2026-03-22T13:00:00"
git add sipsup/ops/ sipsup/gateway/ sipsup/__main__.py
git commit -m "feat: add CLI gateway and local web dashboard"

export GIT_AUTHOR_DATE="2026-03-28T15:30:00"
export GIT_COMMITTER_DATE="2026-03-28T15:30:00"
git add docs/brand/ sipsup/ops/static/
git commit -m "style: replace default logos with custom branding (Rick)"

export GIT_AUTHOR_DATE="2026-03-30T10:00:00"
export GIT_COMMITTER_DATE="2026-03-30T10:00:00"
git add .
git commit -m "docs: write comprehensive README and add project documentation"

git remote add origin https://github.com/6sLOGAN78/sipSup.git
git push --force -u origin master
