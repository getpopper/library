# Ansible

Docker image for [Ansible](https://ansible.com).

## Usage

The [`entrypoint.sh`](./entrypoint.sh) expects an 
`ANSIBLE_SSH_KEY_DATA` variable containing an SSH key that is used to 
connect to ansible hosts. The command invoked by the entrypoint is the 
[`ansible-playbook`][playbook] command.

## Example

```yaml
steps:
- uses: docker://popperized/ansible:v2.9
  args: '-i ansible/hosts.ini ansible/playbooks/dosomething.yml'
  secrets: [ANSIBLE_SSH_KEY_DATA]
```

> **TIP**: to disable host key checking, the workflow can define the 
> `env` varaible:
>
>   ANSIBLE_HOST_KEY_CHECKING = "False"
>
> This variable is **not** used by the image, but it's read by Ansible 
> instead. See the [official documentation][docs] to obtain a list of 
> environment variables that Ansible can read.

### Secrets

  * `ANSIBLE_SSH_KEY_DATA`. **Required** A base64-encoded string 
    containing the private key used to authenticate with hosts 
    referenced in the ansible inventory. Example encoding from a 
    terminal: `cat ~/.ssh/id_rsa | base64`

[playbook]: https://docs.ansible.com/ansible/2.4/ansible-playbook.html
[docs]: https://docs.ansible.com/ansible/latest/reference_appendices/config.html#environment-variables
[galaxy]: https://github.com/ansible/ansible/blob/3b29b50/docs/docsite/rst/reference_appendices/galaxy.rst#installing-multiple-roles-from-a-file
