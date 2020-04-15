# GENI

[GENI](https://www.geni.net) is the Global Environment for Network 
Innovations, a virtual laboratory for networking and distributed 
systems research and education. The container image defined in this 
repository includes [geni-lib][geni-lib], the Python library for 
programatically allocating resources in sites that are part of the 
NSF-sponsored [GENI federation](https://www.geni.net) such as 
[CloudLab](https://cloudlab.us). From the `geni-lib` 
[documentation][geni-docs]:

> Common uses \[of the `geni-lib` python library\] include 
> orchestrating repeatable experiments and writing small tools for 
> inspecting the resources available in a given federation. There are 
> also a number of administrative API handlers available for 
> interacting with software commonly used in experiments - 
> particularly those exposing services to other experimenters.

## Usage

To use this image:

 1. Obtain credentials for the GENI site you want to connect to. 
    Guides for obtaining credentials are available for 
    [`geni.net`][geni-creds] and [`cloudlab.us`][cl-cred]. 

 2. Create a `geni-lib` context. In order to use the `geni-lib` 
    library, it is necessary to create a context (a folder with 
    authentication information) that is used to authenticate against a 
    GENI site. A  `build-context` command is available this purpose 
    (see more [here](#-build-context)).

 2. Execute arbitrary `geni-lib` scripts. Run arbitrary python scripts 
    that make use of the `geni-lib` library, reading the previously 
    built context in order to execute tasks on the GENI site. The 
    `ENTRYPOINT` of this image is the Python interpreter, allowing to 
    specify a script directly as an argument to the image (see more 
    [here](#-execute-script)).

### Example

To use in a [Popper][pp] workflow:

```yaml
steps:

# create the context information (store to `/workspace/.bssw/`)
- uses: popperized/library/geni@59239c3
  runs: build-context
  env:
    GENI_FRAMEWORK: cloudlab
  secrets:
  - GENI_PROJECT
  - GENI_USERNAME
  - GENI_PASSWORD
  - GENI_PUBKEY_DATA
  - GENI_CERT_DATA

# execute python script that invokes geni-lib API functions. The
# invoked scripts make use of the context generated in the previous
# in order to authenticate with GENI sites
- uses: popperized/library/geni@59239c3
  args: ./one-baremetal-node.py
  secrets: [GENI_KEY_PASSPHRASE]

# ...
# one or more following steps that use of allocated resources.
# ...

# lastly, we can release resources
- uses: popperized/library/geni@59239c3
  args: ./release.py
  secrets: [GENI_KEY_PASSPHRASE]
```

The first step builds a context by providing credentials for the GENI 
site (CloudLab in this case) in the form of [step secrets][secrets]. 
These in turn are consumed by the [`build-context`][build-context] 
utility that is installed along with `geni-lib`.

The second  and last steps run arbitrary Python scripts that make use 
of the `geni-lib` library. These scripts load the context created 
previously and interact with a GENI site to obtain resources, fetch 
metadata about available infrastructure, and release resources at the 
end.

The scripts used in the above example can be found [here](./example); 
they are expected to be executed against CloudLab infrastructure. The 
value of `GENI_KEY_PASSPHRASE` in this case is CloudLab's account 
password (see [Execute script section](#-execute-script) for more).

## `build-context`

This is a wrapper to the [`build-context`][build-context] tool 
installed as part of the `geni-lib` Python package. The context is 
stored in the `$PWD/.geni/` folder, where `PWD` is the current working 
directory defined in the container (e.g. via the `--workdir` flag to 
`docker run`).

### Environment

  * `GENI_FRAMEWORK`. **Required** One of `cloudlab`, `emulab`, 
    `portal` and `geni`.

### Secrets

  * `GENI_PROJECT`. **Required** The name of the project.
  * `GENI_USERNAME` **Required** Name of username for GENI account.
  * `GENI_PASSWORD` **Required** Password for user.
  * `GENI_PUBKEY_DATA`. **Required** A base64-encoded string 
    containing the public SSH key for the user authenticating with the 
    site. Example encoding from a terminal: `cat $HOME/.ssh/mykey.pub 
    | base64`.
  * `GENI_CERT_DATA` **Required**. A base64-encoded string containing 
    the certificate issued by the GENI member site. Guides for 
    obtaining credentials are available for [`geni.net`][geni-creds] 
    and [`cloudlab.us`][cl-cred]. Example encoding from a terminal: 
    `cat cloudlab.pem | base64`.

## Execute script

A script provided as argument to the image can load a context (see 
previous sections) by invoking the 
[`geni.util.loadContext()`][loadctx] function and execute arbitrary 
orchestration tasks against GENI infrastructure. Check the [official 
`geni-lib` documentation][geni-docs] for more information on how to 
use `geni-lib`. Concrete examples can be found [here][geni-ex] and 
[here][cl-geni-ex].

> **NOTE**: in non-interactive mode, the `geni.util.loadContext()` 
> function requires the key passphrase (via the `key_passphrase` 
> argument) for the public key provided to the action that builds the 
> context. In those cases, the `GENI_KEY_PASSPHRASE` secret needs to 
> be defined and passed to the `geni.util.loadContext()` function. See 
> an example [here](.ci/teardown.py).

#### Secrets

  * `GENI_KEY_PASSPHRASE`. **Optional** The key passphrase associated 
    to the public key used when building a context.

[from-bundle]: https://geni-lib.readthedocs.io/en/latest/tutorials/portalcontext.html
[geni-docs]: https://geni-lib.rtfd.io/en/latest/
[secrets]: https://popper.readthedocs.io/en/latest/sections/cn_workflows.html#syntax
[build-context]: https://geni-lib.readthedocs.io/en/latest/tutorials/cloudlabcontext.html
[cl-geni-ex]: http://docs.cloudlab.us/geni-lib.html
[geni-ex]: https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/samples/?at=0.9-DEV
[geni-docs]: https://geni-lib.rtfd.io
[geni-lib]: https://bitbucket.org/barnstorm/geni-lib
[pp]: https://github.com/systemslab/popper
[geni-creds]: https://geni-lib.rtfd.io/en/latest/intro/creds/portal.html
[cl-creds]: https://geni-lib.rtfd.io/en/latest/intro/creds/cloudlab.html
[loadctx]: https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/geni/util.py#lines-357
