FROM puppet/puppet-agent-alpine

ENTRYPOINT ["facter"]

COPY Dockerfile /