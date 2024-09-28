# Dependencies

## Python libraries

The following is a list of Python libraries used by LINT:

- results
- requests
- feedparser
- sentence_transformers
- matplotlib
- numpy
    - Only used for debugging the sentence transformer (see module `lint.processors.cat_transformer`)
    - Also required by other dependencies
- scikit-learn
    - Also required by other dependencies

Additionally, if Mistral's online API is to be used, the python client is required as well:
- mistralai
