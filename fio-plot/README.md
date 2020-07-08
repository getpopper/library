# fio plot

Docker image for [fio-plot](https://github.com/louwrentius/fio-plot).

## Example

```yaml
steps:
- uses: docker://getpopper/fio-plot:3.12-2
  args: [fio_plot, -i, /path/to/fio/output, -T, "title", -s, https://louwrentius.com, -L, -r, randread, -t, iops]
```
