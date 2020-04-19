import os

from geni.aggregate import cloudlab
from geni import util


ctx = util.loadContext(os.getcwd() + "/geni-context.json",
                       key_passphrase=os.environ['GENI_KEY_PASSPHRASE'])

print("Available slices: {}".format(ctx.cf.listSlices(ctx).keys()))

if util.sliceExists(ctx, 'popperized'):
    print('Slice exists.')
    print('Removing all existing slivers (errors are ignored)')
    util.deleteSliverExists(cloudlab.Clemson, ctx, 'popperized')
else:
    print("Slice does not exist.")
