Welcome to the repo for my website (which contains a blog, hence the name). It runs on Django with a Wagtail CMS. The frontend is rendered via template; no API here.

The project uses [uv](https://github.com/astral-sh/uv) for package and version management.

Create a virtual environment:
`uv venv --seed --python "$(cat .python-version)" .venv`

Install the dependencies:
`uv pip install -r requirements.txt`

Run the development server:
`cd app && ./manage.py runserver`

Thanks to [Wagtail Bakery](https://github.com/wagtail/bakerydemo) for providing some of the basic elements to get started with.