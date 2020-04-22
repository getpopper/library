import sys

from geni.aggregate import cloudlab
from geni.rspec import pg
from geni import util

experiment_name = 'popperized-geni-example'
command = sys.argv[1]

# load context
ctx = util.loadCtx()

if command == 'apply':
    # create request
    # {
    node = pg.RawPC("node")
    node.disk_image = ("urn:publicid:IDN+clemson.cloudlab.us+image+"
                       "schedock-PG0:ubuntu18-docker")
    node.hardware_type = 'c6320'

    request = pg.Request()
    request.addResource(node)
    # }

    # create slice
    util.createSlice(ctx, experiment_name)

    # create sliver on clemson
    manifest = util.createSliver(ctx, cloudlab.Clemson, experiment_name,
                                 request)

    print(manifest.text)

elif command == 'destroy':

    print("Available slices: {}".format(ctx.cf.listSlices(ctx).keys()))

    if util.sliceExists(ctx, experiment_name):
        print('Slice exists.')
        print('Removing all existing slivers (errors are ignored)')
        util.deleteSliverExists(cloudlab.Clemson, ctx, experiment_name)
    else:
        print("Slice does not exist.")

else:
    raise Exception("Unknown command '{}'".format(command))
