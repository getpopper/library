# How to Contribute

We really appreciate and welcome contributions. All submissions, 
including require review. We use GitHub pull requests for this 
purpose. Consult [GitHub Help][gh] for more information on using pull 
requests.

Every new image should reside on its own folder, with the name of the 
folder taken from the name of the tool or service that the image is 
associated to. The folder needs to contain:

  * A `Dockerfile` that properly pins versions of the tool being 
    containerized.
  * A `README.md` containing the following sections:
      * `Examples`. Showing how the step is used in Popper workflows.
      * `Environment`. If the step reads information from the
        environment, it should be documented here.
      * `Secrets`. If there are secrets that the image expects, as well
        as the format of these, it should be specified in this section.
  * One or more workflow examples in an `examples/` folder. This 
    should ideally be tested by the submitter as we don't run these on 
    Travis CI.

In addition to the above, the pull request needs to also modify the 
[`.travis.yml`](.travis.yml) file so that a new entry to the `env` 
list is added (or modified if the version of an existing image is 
bumped), which is how processing of the image communicated to the CI 
build.

[gh]: https://help.github.com/articles/about-pull-requests/
[dh]: https://hub.docker.com/orgs/getpopper
