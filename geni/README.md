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
    [`geni.net`][geni-creds] and [`cloudlab.us`][cl-creds]. 

 2. Define a list of environment variables that are expected by the 
    [entrypoint](./entrypoint.sh) of the image. See [below](#secrets) 
    for the list of variables that are needed.

 3. Invoke the image and pass a Python script as argument. This script 
    makes use of the `geni-lib` library (see more details 
    [below](#execute-script)).

### Example

For a complete example, take a look at [the `example/` 
folder](./example). To use this image in a [Popper][pp] workflow:

```yaml
steps:

- uses: docker://getpopper/geni:v0.9.9.2
  args: ['./geni_config.py', 'apply']
  secrets:
  - GENI_FRAMEWORK
  - GENI_PROJECT
  - GENI_USERNAME
  - GENI_CERT_DATA
  - GENI_KEY_PASSPHRASE
  - GENI_PUBKEY_DATA


# ...
# one or more steps that use allocated resources.
# ...


# lastly, we can release resources
- uses: docker://getpopper/geni:v0.9.9.2
  args: ['./geni_config.py', 'destroy']
  secrets:
  - GENI_FRAMEWORK
  - GENI_PROJECT
  - GENI_USERNAME
  - GENI_CERT_DATA
  - GENI_KEY_PASSPHRASE
  - GENI_PUBKEY_DATA
```

## Execute scripts

Prior to executing requests to a GENI site using the `geni-lib` 
library, the Python script passed as argument to the image has to load 
a context by invoking the `geni.util.loadCtx()` function as follows:

```python
from geni import util

# ...

ctx = util.loadCtx()

# from this point on, the ctx object is can be passed to functions from
# geni-lib that manipulate (request, release, modify) resources
```

The `loadCtx()` function expects a `GENI_KEY_PASSPHRASE` variable 
containing the passphrase for the given certificate (`GENI_CERT_DATA` 
variable). After the context has been loaded, the script can invoke 
any arbitrary tasks using the `geni-lib` library. Consult the 
[official `geni-lib` documentation][geni-docs] for more information on 
how to use `geni-lib`. Concrete examples can be found [here][geni-ex] 
and [here][cl-geni-ex].

## Secrets

The `ENTRYPOINT` to the image expects the following secrets:

  * `GENI_FRAMEWORK`. **Required** One of `emulab-ch2` (CloudLab), 
    `emulab`, `portal`, or `geni`.
  * `GENI_PROJECT`. **Required** The name of the project, **all lower case**.
  * `GENI_USERNAME` **Required** Name of username for GENI account.
  * `GENI_PUBKEY_DATA`. **Required** A base64-encoded string 
    containing the public SSH key for the user authenticating with the 
    site. Example encoding from a terminal: `cat $HOME/.ssh/mykey.pub 
    | base64`.
  * `GENI_CERT_DATA` **Required**. A base64-encoded string containing 
    the certificate issued by the GENI member site. Guides for 
    obtaining credentials are available for [`geni.net`][geni-creds] 
    and [`cloudlab.us`][cl-cred]. Example encoding from a terminal: 
    `cat cloudlab.pem | base64`.
  * `GENI_KEY_PASSPHRASE`. **Required** The key passphrase associated 
    to the certificate given in `GENI_CERT_DATA`. In the case of 
    CloudLab, this is the password used to login to the web GUI.

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
