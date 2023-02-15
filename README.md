# Enriching Price Transparency Billing Code Data

Insurance companies are now required to publish their rates for the various procedures they cover.
In order to make this resource usable for analysts, we are enriching these data with
addtional external sources. This repo contains some code for getting supplemental data on 
billing codes and merging it on to the innetwork rates file.

## Getting Started

To run this project, you need to have [Python 3.10](https://www.python.org/downloads/release/python-3100/) and 
[Git](https://git-scm.com/downloads) installed. Then you can fork this [repo](https://github.com/mathematica-pub/AST-DS-intern) 
and **set your new repo to private** on Github.

Then you can follow these procedures to install the project and its dependencies locally.
```
> git clone https://github.com/<your_username>/AST-DS-intern # Or whatever your repo's link is
> cd AST-DS-intern
> git checkout -b refactor/modularize_external_file_loading

# if you don't have pipenv installed, do so
> pip install pipenv

> pipenv install 
# if you have more than one version of python installed you may need to add `--python 3.10` to this command

# run the load script
> pipenv run python src/main.py 
```

If any of these commands do not work, please open an issue on the main repository to let us know what
error you experienced.

We have a copy of the database called `original_tutorial.db`. If you need to restore `tutorial.db` you can use that!


## Road Map

This is just a proof of concept, and we need to load many more data sources. We need to refactor
the current solution improve its extensibility and limit code duplication. Priorities:

1. Clean up the spagetti code in `main.py`
2. Move the hard coded values in `main.py` into `config.yaml` and then load it with `utils.load_config()`
3. Create a `SourceDataJob` interface (see potential option in `src/data_jobs/AbstractSourceDataJob.py`) and
refactor the current process in `main.py` to implement the interface for the current two files
4. Come up with something better than a raw sql string? Ideas welcome.

_You should not work on this refactoring for more than two hours._ There is definitely more than 
two hours of work here, so we don't expect you to hit all of these. Just make as much progress as possible!

## Contributing Guidlines
Making sure others can understand your changes and use your code is extremely important. So please:
* Write [semantic commits](https://sparkbox.com/foundry/semantic_commit_messages) 
with clear explanations of your changes
* Use docstrings to explain the API of your functions (See `src/utils.py` for an example). 
* Update this README with instructions for how others should use and extend your solution.
* Add tests to your code so others can verify that their changes are not breaking. 
We generally use pytest. It's installed in the env and there's an example in 'tests/', but
don't waste your time learning a new framework if you haven't used pytest before. Any testing
is better than none!
* Submit a pull request to the main branch of your GitHub repository with your updated branch with an explanation
of the changes you implemented.
* _**Grant the Mathematica reviewers access to your private repo so we can review your PR!**_

Please exercise your creativity and wisdom about what makes for readable, maintainable, and 
extensible code. We are not looking for a reproduction of how we would structure a solution, 
but to see how you go about solving problems in your code. 
