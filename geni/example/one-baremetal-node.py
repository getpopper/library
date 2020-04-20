import os

from geni.aggregate import cloudlab
from geni.rspec import pg
from geni import util

# create request
# {
node = pg.RawPC("node")

node.disk_image = "urn:publicid:IDN+clemson.cloudlab.us+image+schedock-PG0:ubuntu18-docker"
node.hardware_type = 'c6320'

request = pg.Request()
request.addResource(node)
# }

# load context
ctx = util.loadContext(path="/geni-context.json",
                       key_passphrase=os.environ['GENI_KEY_PASSPHRASE'])

# create slice
util.createSlice(ctx, 'popperized')

# create sliver on clemson
manifest = util.createSliver(ctx, cloudlab.Clemson, 'popperized', request)

print(manifest.text)
