# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function

import datetime
import json
import multiprocessing as MP
import os
import os.path
import shutil
import subprocess
import tempfile
import time
import traceback as tb
import zipfile

import six

from .aggregate.apis import ListResourcesError, DeleteSliverError
from geni.minigcf.config import HTTP

HTTP.TIMEOUT = 600


def _getdefault (obj, attr, default):
  if hasattr(obj, attr):
    return obj[attr]
  return default

def checkavailrawpc (context, am):
  """Returns a list of node objects representing available raw PCs at the
given aggregate."""

  avail = []
  ad = am.listresources(context)
  for node in ad.nodes:
    if node.exclusive and node.available:
      if "raw-pc" in node.sliver_types:
        avail.append(node)
  return avail


def _corelogininfo (manifest):
  from .rspec.vtsmanifest import Manifest as VTSM
  from .rspec.pgmanifest import Manifest as PGM

  linfo = []
  if isinstance(manifest, PGM):
    for node in manifest.nodes:
      linfo.extend([(node.client_id, x.username, x.hostname, x.port) for x in node.logins])
  elif isinstance(manifest, VTSM):
    for container in manifest.containers:
      linfo.extend([(container.client_id, x.username, x.hostname, x.port) for x in container.logins])
  return linfo


def printlogininfo (context = None, am = None, slice = None, manifest = None):
  """Prints out host login info in the format:
::
  [client_id][username] hostname:port

If a manifest object is provided the information will be mined from this data,
otherwise you must supply a context, slice, and am and a manifest will be
requested from the given aggregate."""

  if not manifest:
    manifest = am.listresources(context, slice)

  info = _corelogininfo(manifest)
  for line in info:
    print("[%s][%s] %s: %d" % (line[0], line[1], line[2], line[3]))


# You can't put very much information in a queue before you hang your OS
# trying to write to the pipe, so we only write the paths and then load
# them again on the backside
def _mp_get_manifest (context, site, slc, q):
  try:
    # Don't use geni.tempfile here - we don't want them deleted when the child process ends
    # TODO: tempfiles should get deleted when the parent process picks them back up
    mf = site.listresources(context, slc)
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(mf.text)
    path = tf.name
    tf.close()
    q.put((site.name, slc, path))
  except ListResourcesError:
    q.put((site.name, slc, None))
  except Exception:
    tb.print_exc()
    q.put((site.name, slc, None))

def getManifests (context, ams, slices):
  """Returns a two-level dictionary of the form:
::
  {slice_name : { site_object : manifest_object, ... }, ...}

Containing the manifests for all provided slices at all the provided
sites.  Requests are made in parallel and the function blocks until the
slowest site returns (or times out)."""

  sitemap = {}
  for am in ams:
    sitemap[am.name] = am

  q = MP.Queue()
  for site in ams:
    for slc in slices:
      p = MP.Process(target=_mp_get_manifest, args=(context, site, slc, q))
      p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,slc,mpath) = q.get()

    if mpath:
      am = sitemap[site]
      data = open(mpath).read()
      mf = am.amtype.parseManifest(data)
      d.setdefault(slc, {})[sitemap[site]] = mf

  return d


def _mp_get_advertisement (context, site, q):
  try:
    ad = site.listresources(context)
    q.put((site.name, ad))
  except Exception:
    q.put((site.name, None))

def getAdvertisements (context, ams):
  """Returns a dictionary of the form:
::
  { site_object : advertisement_object, ...}

Containing the advertisements for all the requested aggregates.  Requests
are made in parallel and the function blocks until the slowest site
returns (or times out).

.. warning::
  Particularly large advertisements may break the shared memory queue
  used by this function."""


  q = MP.Queue()
  for site in ams:
    p = MP.Process(target=_mp_get_advertisement, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,ad) = q.get()
    d[site] = ad

  return d


def deleteSliverExists(am, context, slice):
  """Attempts to delete all slivers for the given slice at the given AM, suppressing all returned errors."""
  try:
    am.deletesliver(context, slice)
  except DeleteSliverError:
    pass

def _buildaddot(ad, drop_nodes = None):
  """Constructs a dotfile of a topology described by an advertisement rspec.  Only works on very basic GENIv3 advertisements,
  and probably has lots of broken edge cases."""
  # pylint: disable=too-many-branches

  if not drop_nodes:
    drop_nodes = []

  dot_data = []
  dda = dot_data.append # Save a lot of typing

  dda("graph {")

  for node in ad.nodes:
    if node.name in drop_nodes:
      continue

    if node.available:
      dda("\"%s\"" % (node.name))
    else:
      dda("\"%s\" [style=dashed]" % (node.name))

  for link in ad.links:
    if not len(link.interface_refs) == 2:
      print("Link with more than 2 interfaces:")
      print(link.text)

    name_1 = link.interface_refs[0].split(":")[-2].split("+")[-1]
    name_2 = link.interface_refs[1].split(":")[-2].split("+")[-1]

    if name_1 in drop_nodes or name_2 in drop_nodes:
      continue

    dda("\"%s\" -- \"%s\"" % (name_1, name_2))

  dda("}")

  return "\n".join(dot_data)


def builddot (manifests):
  """Constructs a dotfile of the topology described in the passed in manifest list and returns it as a string."""
  # pylint: disable=too-many-branches

  from .rspec import vtsmanifest as VTSM
  from .rspec.pgmanifest import Manifest as PGM

  dot_data = []
  dda = dot_data.append # Save a lot of typing

  dda("digraph {")

  for manifest in manifests:
    if isinstance(manifest, PGM):
      intf_map = {}
      for node in manifest.nodes:
        dda("\"%s\" [label = \"%s\"]" % (node.sliver_id, node.name))
        for interface in node.interfaces:
          intf_map[interface.sliver_id] = (node, interface)

      for link in manifest.links:
        label = link.client_id
        name = link.client_id

        if link.vlan:
          label = "VLAN\n%s" % (link.vlan)
          name = link.vlan

        dda("\"%s\" [label=\"%s\",shape=doublecircle,fontsize=11.0]" % (name, label))

        for ref in link.interface_refs:
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (
            intf_map[ref][0].sliver_id, name,
            intf_map[ref][1].component_id.split(":")[-1]))
          dda("\"%s\" -> \"%s\"" % (name, intf_map[ref][0].sliver_id))


    elif isinstance(manifest, VTSM.Manifest):
      for dp in manifest.datapaths:
        dda("\"%s\" [shape=rectangle];" % (dp.client_id))

      for ctr in manifest.containers:
        dda("\"%s\" [shape=oval];" % (ctr.client_id))

      dda("subgraph cluster_vf {")
      dda("label = \"SSL VPNs\";")
      dda("rank = same;")
      for vf in manifest.functions:
        if isinstance(vf, VTSM.SSLVPNFunction):
          dda("\"%s\" [label=\"%s\",shape=hexagon];" % (vf.client_id, vf.note))
      dda("}")

      # TODO: We need to actually go through datapaths and such, but we can approximate for now
      for port in manifest.ports:
        if isinstance(port, VTSM.GREPort):
          pass
        elif isinstance(port, VTSM.PGLocalPort):
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.shared_vlan,
                                                       port.name))
          dda("\"%s\" -> \"%s\"" % (port.shared_vlan, port.dpname))
        elif isinstance(port, VTSM.InternalPort):
          dp = manifest.findTarget(port.dpname)
          if dp.mirror == port.client_id:
            continue # The other side will handle it, oddly
          # TODO: Handle mirroring into another datapath
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                       port.name))
        elif isinstance(port, VTSM.InternalContainerPort):
          # Check to see if the other side is a mirror into us
          dp = manifest.findTarget(port.remote_dpname)
          if isinstance(dp, VTSM.ManifestDatapath):
            if port.remote_client_id == dp.mirror:
              remote_port_name = port.remote_client_id.split(":")[-1]
              dda("\"%s\" -> \"%s\" [headlabel=\"%s\",taillabel=\"%s\",style=dashed]" % (
                  port.remote_dpname, port.dpname, port.name, remote_port_name))
              continue

          # No mirror, draw as normal
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                       port.name))
        elif isinstance(port, VTSM.VFPort):
          dda("\"%s\" -> \"%s\"" % (port.dpname, port.remote_client_id))
          dda("\"%s\" -> \"%s\"" % (port.remote_client_id, port.dpname))

        elif isinstance(port, VTSM.GenericPort):
          pass
        else:
          continue ### TODO: Unsupported Port Type


  dda("}")

  return "\n".join(dot_data)


class APIEncoder(json.JSONEncoder):
  def default (self, obj): # pylint: disable=E0202
    if hasattr(obj, "__json__"):
      return obj.__json__()
    elif isinstance(obj, set):
      return list(obj)
    return json.JSONEncoder.default(self, obj)


def loadAggregates (path = None):
  from .aggregate.spec import AMSpec
  from . import _coreutil as GCU

  if not path:
    path = GCU.getDefaultAggregatePath()

  ammap = {}
  try:
    obj = json.loads(open(path, "r").read())
    for aminfo in obj["specs"]:
      ams = AMSpec._jconstruct(aminfo)
      am = ams.build()
      if am:
        ammap[am.name] = am
  except IOError:
    pass

  return ammap

def updateAggregates (context, ammap):
  from .aggregate.core import loadFromRegistry

  new_map = loadFromRegistry(context)
  for k,v in new_map.items():
    if k not in ammap:
      ammap[k] = v
  saveAggregates(ammap)

def saveAggregates (ammap, path = None):
  from . import _coreutil as GCU

  if not path:
    path = GCU.getDefaultAggregatePath()

  obj = {"specs" : [x._amspec for x in ammap.values() if x._amspec]}
  with open(path, "w+") as f:
    data = json.dumps(obj, cls=APIEncoder)
    f.write(data)


def loadContext (path = None, key_passphrase = None):
  import geni._coreutil as GCU
  from geni.aggregate import FrameworkRegistry
  from geni.aggregate.context import Context
  from geni.aggregate.user import User

  if path is None:
    path = GCU.getDefaultContextPath()
  else:
    path = os.path.expanduser(path)

  obj = json.load(open(path, "r"))

  version = _getdefault(obj, "version", 1)

  if key_passphrase is True:
    import getpass
    key_passphrase = getpass.getpass("Private key passphrase: ")

  if version == 1:
    cf = FrameworkRegistry.get(obj["framework"])()
    cf.cert = obj["cert-path"]
    if key_passphrase:
      if six.PY3:
        key_passphrase = bytes(key_passphrase, "utf-8")
      cf.setKey(obj["key-path"], key_passphrase)
    else:
      cf.key = obj["key-path"]

    user = User()
    user.name = obj["user-name"]
    user.urn = obj["user-urn"]
    user.addKey(obj["user-pubkeypath"])

    context = Context()
    context.addUser(user)
    context.cf = cf
    context.project = obj["project"]
    context.path = path

  elif version == 2:
    context = Context()

    fobj = obj["framework-info"]
    cf = FrameworkRegistry.get(fobj["type"])()
    cf.cert = fobj["cert-path"]
    if key_passphrase:
      cf.setKey(fobj["key-path"], key_passphrase)
    else:
      cf.key = fobj["key-path"]
    context.cf = cf
    context.project = fobj["project"]
    context.path = path

    ulist = obj["users"]
    for uobj in ulist:
      user = User()
      user.name = uobj["username"]
      user.urn = _getdefault(uobj, "urn", None)
      klist = uobj["keys"]
      for keypath in klist:
        user.addKey(keypath)
      context.addUser(user)

  from cryptography import x509
  from cryptography.hazmat.backends import default_backend
  cert = x509.load_pem_x509_certificate(open(context._cf.cert, "rb").read(), default_backend())
  if cert.not_valid_after < datetime.datetime.now():
    print("***WARNING*** Client SSL certificate supplied in this context is expired")
  return context


def hasDataContext ():
  import geni._coreutil as GCU

  path = GCU.getDefaultContextPath()
  return os.path.exists(path)


class MissingPublicKeyError(Exception):
  def __str__ (self):
    return "Your bundle does not appear to contain an SSH public key.  You must supply a path to one."


class PathNotFoundError(Exception):
  def __init__ (self, path):
    super(PathNotFoundError, self).__init__()
    self._path = path

  def __str__ (self):
    return "The path %s does not exist." % (self._path)

def _find_ssh_keygen ():
  PATHS = ["/usr/bin/ssh-keygen", "/bin/ssh-keygen", "/usr/sbin/ssh-keygen", "/sbin/ssh-keygen"]
  for path in PATHS:
    if os.path.exists(path):
      return path

MAKE_KEYPAIR = (-1, 1)

def buildContextFromBundle (bundle_path, pubkey_path = None, cert_pkey_path = None):
  import geni._coreutil as GCU

  HOME = os.path.expanduser("~")

  # Create the .bssw directories if they don't exist
  DEF_DIR = GCU.getDefaultDir()

  zf = zipfile.ZipFile(os.path.expanduser(bundle_path))

  zip_pubkey_path = None
  if pubkey_path is None or pubkey_path == MAKE_KEYPAIR:
    # search for pubkey-like file in zip
    for fname in zf.namelist():
      if fname.startswith("ssh/public/") and fname.endswith(".pub"):
        zip_pubkey_path = fname
        break

    if not zip_pubkey_path and pubkey_path != MAKE_KEYPAIR:
      raise MissingPublicKeyError()

  # Get URN/Project/username from omni_config
  urn = None
  project = None

  oc = zf.open("omni_config")
  for l in oc.readlines():
    if l.startswith("urn"):
      urn = l.split("=")[1].strip()
    elif l.startswith("default_project"):
      project = l.split("=")[1].strip()

  uname = urn.rsplit("+")[-1]

  # Create .ssh if it doesn't exist
  try:
    os.makedirs("%s/.ssh" % (HOME), 0o775)
  except OSError:
    pass

  # If a pubkey wasn't supplied on the command line, we may need to install both keys from the bundle
  # This will catch if creation was requested but failed
  pkpath = pubkey_path
  if not pkpath or pkpath == MAKE_KEYPAIR:
    found_private = False

    if "ssh/private/id_geni_ssh_rsa" in zf.namelist():
      found_private = True
      if not os.path.exists("%s/.ssh/id_geni_ssh_rsa" % (HOME)):
        # If your umask isn't already 0, we can't safely create this file with the right permissions
        with os.fdopen(os.open("%s/.ssh/id_geni_ssh_rsa" % (HOME), os.O_WRONLY | os.O_CREAT, 0o600), "w") as tf:
          tf.write(zf.open("ssh/private/id_geni_ssh_rsa").read())

    if zip_pubkey_path:
      pkpath = "%s/.ssh/%s" % (HOME, zip_pubkey_path[len('ssh/public/'):])
      if not os.path.exists(pkpath):
        with open(pkpath, "w+") as tf:
          tf.write(zf.open(zip_pubkey_path).read())

    # If we don't find a proper keypair, we'll make you one if you asked for it
    # This preserves your old pubkey if it existed in case you want to use that later
    if not found_private and pubkey_path == MAKE_KEYPAIR:
      keygen = _find_ssh_keygen()
      subprocess.call("%s -t rsa -b 2048 -f ~/.ssh/genilib_rsa -N ''" % (keygen), shell = True)
      pkpath = os.path.expanduser("~/.ssh/genilib_rsa.pub")
  else:
    pkpath = os.path.expanduser(pubkey_path)
    if not os.path.exists(pkpath):
      raise PathNotFoundError(pkpath)

  # We write the pem into 'private' space
  zf.extract("geni_cert.pem", DEF_DIR)

  if cert_pkey_path is None:
    ckpath = "%s/geni_cert.pem" % (DEF_DIR)
  else:
    # Use user-provided key path instead of key inside .pem
    ckpath = os.path.expanduser(cert_pkey_path)
    if not os.path.exists(ckpath):
      raise PathNotFoundError(ckpath)

  cdata = {}
  cdata["framework"] = "portal"
  cdata["cert-path"] = "%s/geni_cert.pem" % (DEF_DIR)
  cdata["key-path"] = ckpath
  cdata["user-name"] = uname
  cdata["user-urn"] = urn
  cdata["user-pubkeypath"] = pkpath
  cdata["project"] = project
  json.dump(cdata, open("%s/context.json" % (DEF_DIR), "w+"))


def _buildContext (framework, cert_path, key_path, username, user_urn, pubkey_path, project, path=None):
  import geni._coreutil as GCU

  # Create the .bssw directories if they don't exist
  DEF_DIR = GCU.getDefaultDir()

  new_cert_path = "%s/%s" % (DEF_DIR, os.path.basename(cert_path))
  shutil.copyfile(cert_path, new_cert_path)

  if key_path != cert_path:
    new_key_path = "%s/%s" % (DEF_DIR, os.path.basename(key_path))
    shutil.copyfile(key_path, new_key_path)
  else:
    new_key_path = new_cert_path

  if not path:
    path = "%s/context.json" % (DEF_DIR)

  cdata = {}
  cdata["framework"] = framework
  cdata["cert-path"] = new_cert_path
  cdata["key-path"] = new_key_path
  cdata["user-name"] = username
  cdata["user-urn"] = user_urn
  cdata["user-pubkeypath"] = pubkey_path
  cdata["project"] = project
  json.dump(cdata, open(path, "w+"))


def sliceExists(ctx, slice):
    """Queries the federation to see if the given slice exists
    """
    slice_id = (
        "urn:publicid:IDN+emulab.net:{}+slice+{}"
    ).format(ctx.project, slice)
    if slice_id in ctx.cf.listSlices(ctx):
        return True
    return False


def createSlice(ctx, slice, expiration=120, renew_if_exists=False):
    """Creates slice. Optionally, if slice already exists, it renews its
    expiration time if 'renew_if_exists=True'.
    """
    slice_id = (
        "urn:publicid:IDN+emulab.net:{}+slice+{}"
    ).format(ctx.project, slice)

    exp = (datetime.datetime.now() + datetime.timedelta(minutes=expiration))

    print("Available slices: {}".format(ctx.cf.listSlices(ctx).keys()))

    if slice_id in ctx.cf.listSlices(ctx):
        print("Slice {} exists".format(slice_id))
        if renew_if_exists:
            print("Renewing slice for {} more minutes".format(expiration))
            ctx.cf.renewSlice(ctx, slice, exp=exp)
    else:
        print("Creating slice {} ({} mins)".format(slice_id, expiration))
        ctx.cf.createSlice(ctx, slice, exp=exp)


def createSliver(ctx, am, slice, request, timeout=15):
    """Creates a sliver on given aggregate, using the given request. Returns
    a manifest for the sliver. Waits 'timeout' minutes for the sliver to be in
    'ready' state before returning. If timeout is reached and clenup is 'True',
    it tries to delete the sliver before returning.
    """

    manifest = None

    print("Creating sliver on {}".format(am.name))

    manifest = am.createsliver(ctx, slice, request)

    time.sleep(60)

    print("Waiting for sliver to come up online ({} mins max)".format(timeout))

    time_limit = time.time() + 60 * timeout

    while True:
        time.sleep(60)

        status = am.sliverstatus(ctx, slice)

        if status['pg_status'] == 'ready':
            break

        if time.time() > time_limit:
            raise Exception("Time limit ({} mins) reached!".format(timeout))

    return manifest


def toAnsibleInventory(manifest, groups={}, hostsfile='./hosts',
                       format='ini', append=False):
    """Creates an Ansible inventory file from a given manifest in the specified
    format. For INI files, the output format is the following:

      <name> ansible_host=<fqdn> ansible_user=<username> ansible_become=True
      ...
      ...

      <groups>

    where:

      - name: name of the node.
      - fqdn: fqdn of the node.
      - username: the username as reported by node.logins[0].
      - groups: the contents of the given groups dictionary. For example:

          {
            servers: ['s1', 's2'],
            clients: ['c1', 'c2'],
          }

        will result in the following for INI:

          [servers]
          s1
          s2

          [clients]
          c1
          c2

    When format==yaml, the inventory is an equivalent of the above but in YAML
    format.
    """

    hostsfile = hostsfile + ('.ini' if format == "ini" else ".yaml")

    with open(hostsfile, 'a' if append else 'w') as f:

        if format == 'yaml':
            f.write('all:\n  hosts:\n')

        for i, n in enumerate(manifest.nodes):
            if format == 'yaml':
                f.write('    {}:\n'.format(n.name))
                f.write('      {}: {}\n'.format('ansible_host', n.hostfqdn))
                f.write('      {}: {}\n'.format('ansible_user',
                                                n.logins[0].username))
                f.write('      ansible_become: true\n')
            else:
                f.write(n.name)
                f.write(' {}={}'.format('ansible_host', n.hostfqdn))
                f.write(' {}={}'.format('ansible_user', n.logins[0].username))
                f.write(' ansible_become=True\n')

        if format == 'yaml':
            f.write('  children:\n')
            for group, hosts in groups.items():
                f.write('    {}:\n      hosts:\n'.format(group))
                for h in hosts:
                    f.write('        {}:\n'.format(h))
        else:
            for group, hosts in groups.items():
                f.write('[{}]\n'.format(group))
                f.write('\n'.join(hosts))
                f.write('\n')


def xmlManifestToAnsibleInventory(manifest, groups={}, hostsfile='./hosts',
                                  format='ini', append=False):

    """Same as toAnsibleInventory but from an XML file
    """
    from .rspec.pgmanifest import Manifest as PGM

    toAnsibleInventory(PGM(manifest), groups, hostsfile, format, append)
