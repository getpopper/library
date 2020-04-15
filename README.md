# Popper steps

This repository contains source code of docker images that are used in 
[Popper][pp] workflows.

## How to use a step

Once you find an image that suits your needs, you can use it in a 
workflow by adding it as a step:

```yaml
steps:
- uses: popperized/<STEP-NAME>@<TAG>
  args: ['arguments', 'for', 'the', 'step']
```

Additional `env` and `secrets` options for a step might be required. 
The `README` of for an image might contain `Environment` and `Secrets` 
sections describing how to provide this extra information that is 
specific to a step. For information about which tag to use, see the 
corresponding repository at the [Dockerhub Registry][dh].

## Contributing

We welcome contributions! See [CONTRIBUTING](CONTRIBUTING.md) for more 
information on how to get started.

## Support

To file issues and feature requests against these images, or the usage 
of these build steps [create an issue in this 
repo](https://github.com/popperized/library/issues/new).

If you are experiencing an issue with Popper or have a feature request 
related to Popper, please file an issue against the [Popper 
Repository](https://github.com/systemslab/popper/issues/new).

## License

[MIT](LICENSE). Please see additional information in each 
subdirectory.

[pp]: https://github.com/systemslab/popper
[dh]: https://hub.docker.com/orgs/popperized
