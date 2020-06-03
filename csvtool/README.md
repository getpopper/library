# Ansible

Docker image for [CSVTool](https://github.com/Chris00/ocaml-csv).

## Example

```yaml
steps:
- uses: docker://getpopper/csvtool:2.4
  args: [csvtool, transpose, input.csv, -o, ouput.csv]
```
