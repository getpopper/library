# Popper workflow for GENI example

> **NOTE**: To run this example you need [Popper][pp] and 
> [Docker][docker] installed on your machine as well as a 
> [CloudLab][cl] account.

This example showcases how to request a node on CloudLab. Start by 
copying the `wf.yml` file to your project folder first, as well as the 
Python scripts included in this folder. Take a look at the 
[`one-baremetal-node.py`](./one-baremetal-node.py) script for details 
on what is done in this example.

Before you can execute the example using Popper, you need to define 
the following variables in your environment, substituting with values 
corresponding to your your CloudLab account. See [here][cl-creds] for 
a information on how to obtain a certificate for CloudLab.

```bash
cd myproject/

export GENI_FRAMEWORK="emulab-ch2"
export GENI_PROJECT=<cloudlab-project-name>
export GENI_USERNAME=<cloudlab-username>
export GENI_KEY_PASSPHRASE='<cloudlab-password>'
export GENI_PUBKEY_DATA=$(cat /path/to/mykey.pub | base64)
export GENI_CERT_DATA=$(cat /path/to/cert.pem | base64)
```

Note that in the above we enclose the `GENI_KEY_PASSPHRASE` variable 
in single quotes to avoid having the shell expand certain characters 
such as `$`. After the above is defined, you can executed the workflow 
by running:

```bash
popper run -f wf.yml
```

[pp]: https://github.com/systemslab/popper
[docker]: https://docs.docker.com/get-docker/
[cl]: https://cloudlab.us
[cl-creds]: https://geni-lib.rtfd.io/en/latest/intro/creds/cloudlab.html
