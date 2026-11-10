# notebook

A small local CLI that stores note titles in a JSON file.

```sh
node notebook.js add "Buy milk"
node notebook.js --version
```

Data lives in `~/.notebook.json`. Set `NOTEBOOK_FILE=/path/to/file.json` to use an isolated data file.
