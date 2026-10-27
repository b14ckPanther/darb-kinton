# Darb Kinton brand directions, rendered in Blender Cycles. Everything is built here in code: no imported art.
#   blender -b -P kinton.py -- <direction> <out.png> [size] [samples]
#   directions: vapor | threads | ingot | crest
import bpy, sys, math, json, random
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
D, OUT = argv[0], argv[1]
SIZE = int(argv[2]) if len(argv) > 2 else 1024
SAMPLES = int(argv[3]) if len(argv) > 3 else 256
T = json.loads((Path(__file__).resolve().parents[2] / 'src' / 'tokens.json').read_text())
rng = random.Random(T['render']['seed'])


def lin(hexstr, k=1.0):
    """sRGB hex to linear RGBA, optionally scaled."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


COL = {k: v['hex'] for k, v in T['color'].items()}

# ---------- scene, renderer, colour ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU unavailable, using CPU:', e)
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.volume_step_rate = 1.0
scene.cycles.max_bounces = 12
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
for look in ('AgX - Medium High Contrast', 'AgX - Punchy', 'AgX - Base Contrast'):
    try:
        scene.view_settings.look = look
        break
    except TypeError:
        pass
coll = scene.collection


def link(obj):
    coll.objects.link(obj)
    return obj


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return m, nt, out


def metal(name, hexstr, rough=0.22, aniso=0.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def glossy(name, hexstr, rough=0.3, coat=1.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.06
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def emissive(name, hexstr, strength):
    m, nt, out = node_mat(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = lin(hexstr)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def vapor_mat(name, density=14.0, glow=0.35, scale=2.6, along=None):
    """Principled Volume eroded by fractal noise, so edges are wisps rather than a hard skin.
    `along` = 'x' fades density along the object's generated X (for trails)."""
    m, nt, out = node_mat(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = scale
    nz.inputs['Detail'].default_value = 12
    nz.inputs['Roughness'].default_value = 0.62
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[1].position = 0.68
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = density
    nt.links.new(ramp.outputs['Color'], mul.inputs[0])
    dens = mul
    if along:
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6
        nt.links.new(sep.outputs['X'], pw.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
        nt.links.new(mul.outputs[0], m2.inputs[0]); nt.links.new(pw.outputs[0], m2.inputs[1])
        dens = m2
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = lin(COL['nimbus'])
    v.inputs['Anisotropy'].default_value = 0.35
    v.inputs['Emission Color'].default_value = lin(COL['gold'])
    v.inputs['Emission Strength'].default_value = glow
    nt.links.new(dens.outputs[0], v.inputs['Density'])
    nt.links.new(v.outputs[0], out.inputs['Volume'])
    return m


def to_mesh(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active


def nimbus_hull(name, length=3.0, h=0.7, loc=(0, 0, 0), rot=0.0, res=0.035):
    """The cloud's envelope from metaballs: round, high crown at the front, thinning to a tail behind.
    The volume material erodes it into vapour; displacement breaks the silhouette."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res
    mb.threshold = 0.6
    ob = link(bpy.data.objects.new(name, mb))
    n = 14
    for i in range(n):
        t = i / (n - 1)
        r = h * (0.16 + 0.84 * math.sin(math.pi * (0.06 + 0.6 * t)))
        e = mb.elements.new(); e.co = (-length / 2 + length * t, 0, r * 0.35); e.radius = r * 1.25
    for t, k in ((0.5, 0.9), (0.72, 1.15), (0.9, 0.85)):
        e = mb.elements.new(); e.co = (-length / 2 + length * t, rng.uniform(-.1, .1), h * 0.62 + h * k * 0.4); e.radius = h * k * 1.2
    ob = to_mesh(ob)
    tex = bpy.data.textures.new(name + '-clouds', 'CLOUDS'); tex.noise_scale = 0.35; tex.noise_depth = 4
    d = ob.modifiers.new('break', 'DISPLACE'); d.texture = tex; d.strength = 0.22; d.mid_level = 0.5
    ob.location = loc
    ob.rotation_euler = (0, rot, 0)  # Z is up, the camera looks along +Y, so Y rotation tilts it in the picture
    bpy.context.view_layer.update()
    return ob


def vapour(hull, name, density=6.0, glow=0.5, push=0.22, voxel=0.025, scale=1.6, detail=2.4):
    """Turns a hull mesh into a real cloud: mesh-to-volume, then displaced by a cloud texture so the edges
    tear into wisps; the shader multiplies the voxel density by fine noise for billowing detail."""
    vol = link(bpy.data.objects.new(name, bpy.data.volumes.new(name)))
    m2v = vol.modifiers.new('fill', 'MESH_TO_VOLUME'); m2v.object = hull
    m2v.resolution_mode = 'VOXEL_SIZE'; m2v.voxel_size = voxel; m2v.interior_band_width = 0.2; m2v.density = 1.0
    tex = bpy.data.textures.new(name + '-billow', 'CLOUDS'); tex.noise_scale = 0.45; tex.noise_depth = 5
    dsp = vol.modifiers.new('tear', 'VOLUME_DISPLACE'); dsp.texture = tex; dsp.strength = push; dsp.texture_mid_level = (0.5, 0.5, 0.5)
    hull.hide_render = True
    m, nt, out = node_mat(name + '-m')
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'density'
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale * detail; nz.inputs['Detail'].default_value = 14; nz.inputs['Roughness'].default_value = 0.6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['From Min'].default_value = 0.38; ramp.inputs['From Max'].default_value = 0.66
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
    a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; nt.links.new(at.outputs['Fac'], a.inputs[0]); nt.links.new(ramp.outputs[0], a.inputs[1])
    b = nt.nodes.new('ShaderNodeMath'); b.operation = 'MULTIPLY'; b.inputs[1].default_value = density; nt.links.new(a.outputs[0], b.inputs[0])
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = lin('#F2C46A')
    v.inputs['Anisotropy'].default_value = 0.4
    v.inputs['Emission Color'].default_value = lin(COL['gold'])
    nt.links.new(b.outputs[0], v.inputs['Density'])
    e = nt.nodes.new('ShaderNodeMath'); e.operation = 'MULTIPLY'; e.inputs[1].default_value = glow; nt.links.new(a.outputs[0], e.inputs[0])
    nt.links.new(e.outputs[0], v.inputs['Emission Strength'])
    nt.links.new(v.outputs[0], out.inputs['Volume'])
    vol.data.materials.append(m)
    return vol


def tube_mesh(name, pts, radii, bevel):
    """A tapered tube as a mesh, used as a hull for vapour trails."""
    ob = tube(name, pts, radii, emissive(name + '-x', '#000000', 0), bevel=bevel, res=8)
    ob = to_mesh(ob)
    return ob


def tube(name, pts, radii, mat, bevel=1.0, res=6):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = bevel; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co, r in zip(sp.points, pts, radii):
        p.co = (*co, 1.0); p.radius = r
    sp.use_endpoint_u = True; sp.order_u = 4
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def world(stars=True):
    w = bpy.data.worlds.new('night'); scene.world = w; w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = lin(COL['forest'], 0.5); ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].color = lin(COL['night'], 0.6); ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.6
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    if stars:
        vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 260
        nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
        st = nt.nodes.new('ShaderNodeMath'); st.operation = 'LESS_THAN'; st.inputs[1].default_value = 0.018
        nt.links.new(vor.outputs['Distance'], st.inputs[0])
        sb = nt.nodes.new('ShaderNodeBackground'); sb.inputs['Color'].default_value = (1, .95, .85, 1); sb.inputs['Strength'].default_value = 1.4
        add = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(st.outputs[0], add.inputs['Fac']); nt.links.new(bg.outputs[0], add.inputs[1]); nt.links.new(sb.outputs[0], add.inputs[2])
        nt.links.new(add.outputs[0], out.inputs['Surface'])
    else:
        nt.links.new(bg.outputs[0], out.inputs['Surface'])


def area(name, loc, target, power, hexstr, size=3.0, shape='DISK'):
    li = bpy.data.lights.new(name, 'AREA'); li.energy = power; li.color = lin(hexstr)[:3]; li.size = size; li.shape = shape
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def point(name, loc, power, hexstr, radius=0.2):
    li = bpy.data.lights.new(name, 'POINT'); li.energy = power; li.color = lin(hexstr)[:3]; li.shadow_soft_size = radius
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    return ob


def camera(loc, target, lens=60):
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    ob = link(bpy.data.objects.new('cam', cam)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob


# ---------- shared marks ----------
def poly_curve(name, polys, extrude, bevel, mat, res=8):
    """Flat outlines (outer + nested holes) extruded and bevelled like cast metal."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = res
    for poly in polys:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 1)
        for p, (x, y) in zip(sp.points, poly):
            p.co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def arcs(cx, cy, r, a0, a1, n=28):
    return [(cx + math.cos(a0 + (a1 - a0) * i / n) * r, cy + math.sin(a0 + (a1 - a0) * i / n) * r) for i in range(n + 1)]


def spiral(x, y, r0, turns, w=0.034, n=140):
    f = lambda t, k: (x + math.cos(math.pi / 2 + t * turns * 2 * math.pi) * (r0 * (1 - t * .85) + k), y + math.sin(math.pi / 2 + t * turns * 2 * math.pi) * (r0 * (1 - t * .85) + k))
    return [f(i / n, w) for i in range(n + 1)] + [f(i / n, -w * (1 - i / n * .5)) for i in reversed(range(n + 1))]


def keyhole(x, y, r=0.17, n=40):
    """A keyhole: round head, tapered slot below."""
    a = math.asin(0.45)
    head = [(x + math.cos(t) * r, y + math.sin(t) * r) for t in (-math.pi / 2 + a + (2 * math.pi - 2 * a) * i / n for i in range(n + 1))]
    return head + [(x - r * 0.62, y - r * 2.6), (x + r * 0.62, y - r * 2.6)]


CX, CY = 0.45, 0.15
CLOUD = [(CX - 1.05, CY - 0.35)] + arcs(CX - 0.62, CY + 0.08, 0.5, math.pi * 1.05, math.pi * 0.32) \
    + arcs(CX + 0.05, CY + 0.42, 0.55, math.pi * 0.95, math.pi * 0.12) + arcs(CX + 0.68, CY - 0.02, 0.48, math.pi * 0.62, -math.pi * 0.42)


def tails(n=3):
    out = []
    for i in range(n):
        y0, ln, th = CY - 0.12 - i * 0.2, 1.55 - i * 0.28, 0.085 - i * 0.012
        x0 = CX - 0.95
        top = [(x0 - ln * t, y0 + th * (1 - t) - (0.38 + i * .05) * t ** 2) for t in (j / 30 for j in range(31))]
        bot = [(x0 - ln * t, y0 - th * (1 - t) - (0.38 + i * .05) * t ** 2) for t in (j / 30 for j in reversed(range(31)))]
        out.append(top + bot)
    return out


def medallion(r=2.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r, depth=0.2, location=(0, 0, 0))
    disc = bpy.context.active_object
    bv = disc.modifiers.new('b', 'BEVEL'); bv.width = 0.05; bv.segments = 6
    bpy.ops.object.shade_smooth()
    disc.data.materials.append(glossy('lacquer', '#04140C', 0.32, 1.0))
    bpy.ops.mesh.primitive_torus_add(major_radius=r - 0.19, minor_radius=0.05, major_segments=256, minor_segments=24, location=(0, 0, 0.1))
    bpy.ops.object.shade_smooth()
    bpy.context.active_object.data.materials.append(metal('gold', COL['gold'], 0.16))


def jewel_lights():
    area('key', (-3, -3, 7), (0, 0, 0), 900, COL['goldLight'], 2.5)
    area('strip', (4, 1, 4), (0, 0, 0), 350, COL['ivory'], 0.6)
    area('rim', (0, 5, 2), (0, 0, 0), 500, COL['sky'], 4)
    area('face', (0, 3.2, 10.5), (0, 0, 0), 110, COL['goldLight'], 7)


def slab(name, w, h, d, bevel, mat, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object; ob.name = name; ob.scale = (w, h, d)
    bpy.ops.object.transform_apply(scale=True)
    bv = ob.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = 8; bv.limit_method = 'NONE'
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


# ---------- directions ----------
if D == 'keyhole':
    # A "Only the pure of heart can ride it": the nimbus with a keyhole through its heart, lit from inside.
    # Kinton carries only the pure of heart; this cloud opens only for your own devices (end-to-end encryption).
    world(stars=False)
    gold_m = metal('gold', COL['gold'], 0.16)
    k = keyhole(CX + 0.05, CY + 0.3, 0.15)
    poly_curve('crest', [CLOUD, spiral(CX - 0.62, CY + 0.08, 0.3, 1.35), spiral(CX + 0.68, CY - 0.02, 0.28, 1.35), k], 0.09, 0.028, gold_m).location.z = 0.14
    for i, t in enumerate(tails()):
        poly_curve(f'tail{i}', [t], 0.06, 0.018, gold_m).location.z = 0.14
    glow = poly_curve('light', [keyhole(CX + 0.05, CY + 0.3, 0.2)], 0.005, 0.0, emissive('within', COL['goldLight'], 40))
    glow.location.z = 0.11
    medallion(); jewel_lights()
    camera((0, -2.4, 11), (0, 0, 0), 62)

elif D == 'direct':
    # B "Straight there": your phone to your laptop on one gold arc, nothing in between. Peer to peer.
    world()
    body = metal('graphite', '#2A3430', 0.28)
    glass = glossy('screen', '#06140E', 0.06, 1.0)
    lit = emissive('lit', COL['forest'], 1.6)
    phone = link(bpy.data.objects.new('phone', None)); phone.location = (-1.8, 0, -0.75); phone.rotation_euler = (0, 0, math.radians(22))
    slab('ph', 0.66, 0.1, 1.32, 0.1, body).parent = phone
    sc = slab('phs', 0.58, 0.02, 1.22, 0.08, lit, (0, -0.045, 0)); sc.parent = phone
    lap = link(bpy.data.objects.new('laptop', None)); lap.location = (1.45, 0.2, -1.35); lap.rotation_euler = (0, 0, math.radians(-24))
    slab('base', 2.1, 1.4, 0.07, 0.05, body, (0, 0, 0)).parent = lap
    lid = link(bpy.data.objects.new('lid', None)); lid.parent = lap; lid.location = (0, 0.7, 0.035); lid.rotation_euler = (math.radians(-14), 0, 0)
    slab('lidb', 2.1, 0.05, 1.36, 0.05, body, (0, 0, 0.68)).parent = lid
    ls = slab('lids', 1.96, 0.02, 1.2, 0.03, lit, (0, -0.032, 0.7)); ls.parent = lid
    bpy.context.view_layer.update()
    a_ = sc.matrix_world @ Vector((0, -0.05, 0.2))
    b_ = ls.matrix_world @ Vector((0, -0.05, 0.05))
    apex = a_.lerp(b_, 0.45) + Vector((0, -0.2, 2.2))
    curve = [a_ + (apex - a_) * (2 * t * (1 - t)) * 2 * 0 + (a_ * (1 - t) ** 2 + apex * 2 * t * (1 - t) + b_ * t ** 2 - a_) for t in (i / 24 for i in range(25))]
    pts = [tuple(v) for v in curve]
    tube('core', pts, [0.4 + 0.6 * math.sin(math.pi * i / 24) for i in range(25)], emissive('core', COL['gold'], 9), bevel=0.012)
    at = 17
    cloud = nimbus_hull('nimbus', 1.5, 0.38, loc=tuple(Vector(pts[at]) + Vector((0, 0, -0.18))), rot=0.4)
    vapour(cloud, 'carry', 14, 0.15, push=0.12, voxel=0.015)
    vapour(tube_mesh('trailhull', pts[4:at], [0.05 + 0.95 * i / (at - 5) for i in range(at - 4)], 0.16), 'trail', 4, 1.3, push=0.12, scale=2.4)
    area('key', (-4, -6, 6), (0, 0, -0.5), 1500, COL['goldLight'], 4)
    area('rim', (4, 5, 3), (0, 0, -0.5), 900, COL['sky'], 3)
    camera((0, -11, 1.6), (-0.1, 0, -0.15), 74)

elif D == 'sealed':
    # C "Sealed in flight": your file folded and closed with a gold seal, carried by the nimbus.
    # Nobody on the way (not even your own server) can open it.
    world()
    cloud = nimbus_hull('carrier', 3.2, 0.6, loc=(0.2, 0, -1.0), rot=-0.06)
    vapour(cloud, 'carrierv', 14, 0.3)
    point('under', (0.4, -0.3, -0.75), 140, COL['goldLight'], 0.6)
    paper = glossy('paper', '#CFC3A6', 0.55, 0.2)
    W, H, F = 1.3, 1.65, 0.36
    env = poly_curve('file', [[(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2 - F), (W / 2 - F, H / 2), (-W / 2, H / 2)]], 0.025, 0.012, paper)
    fold = poly_curve('fold', [[(W / 2 - F, H / 2), (W / 2 - F, H / 2 - F), (W / 2, H / 2 - F)]], 0.008, 0.006, glossy('paper2', '#D9CCAE', 0.6, 0.1))
    fold.parent = env; fold.location.z = 0.035
    # the seal: a thick gold coin with the cloud crest struck into it
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.36, depth=0.09, location=(0, -0.05, 0.08))
    coin = bpy.context.active_object; coin.rotation_euler = (math.radians(90), 0, 0); coin.rotation_euler = (0, 0, 0)
    bv = coin.modifiers.new('b', 'BEVEL'); bv.width = 0.03; bv.segments = 6
    bpy.ops.object.shade_smooth(); coin.data.materials.append(metal('seal', COL['gold'], 0.22)); coin.parent = env
    mini = poly_curve('emblem', [[((x - CX) * 0.2, (y - CY) * 0.2 + 0.0) for x, y in CLOUD]], 0.012, 0.006, metal('goldDeep', COL['goldDeep'], 0.3))
    mini.parent = env; mini.location = (0.02, -0.07, 0.135)
    for i, t in enumerate(tails()):
        tm = poly_curve(f'mt{i}', [[((x - CX) * 0.2, (y - CY) * 0.2) for x, y in t]], 0.008, 0.004, metal('goldDeep', COL['goldDeep'], 0.3)); tm.parent = env; tm.location = (0.02, -0.07, 0.135)
    env.location = (0.45, 0, 0.4); env.rotation_euler = (math.radians(90 - 8), math.radians(-6), math.radians(-18))
    tail = cloud.matrix_world @ Vector((-1.55, 0, 0.1))
    vapour(tube_mesh('trailhull', [(-4.2, 0.4, -2.2), (-3.2, 0.3, -1.6), (-2.2, 0.1, -1.1), tuple(tail)], [0.05, 0.35, 0.75, 1.0], 0.3), 'trail', 4, 1.4, push=0.3, scale=2.4)
    area('key', (-4, -6, 6), (0.4, 0, 0.3), 1300, COL['goldLight'], 3)
    area('fill', (4, -5, 1), (0.4, 0, 0.3), 380, COL['ivory'], 4)
    area('rim', (3, 5, 4), (0.4, 0, 0.3), 1100, COL['sky'], 3)
    camera((0.6, -11.5, 0.8), (-0.3, 0, -0.35), 72)

elif D == 'arc':
    # D "Drop it, it flies": the app's own gesture as a mark. Two devices (two gold beads) and the throw
    # between them; the nimbus rides the top of the arc.
    world(stars=False)
    gold_m = metal('gold', COL['gold'], 0.16)
    L, R, Y0 = (-1.3, -0.95), (1.3, -0.5), -0.95
    for x, y in (L, R):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=0.24, location=(x, y, 0.3))
        bpy.ops.object.shade_smooth(); bpy.context.active_object.data.materials.append(gold_m)
    P = lambda t: (L[0] + (R[0] - L[0]) * t, L[1] + 0.3 + (R[1] - L[1]) * t + 1.6 * 4 * t * (1 - t))
    ride = 0.62
    for i in range(22):  # the path already flown: dots that grow toward the cloud
        t = ride * (i + 0.5) / 22
        x, y = P(t)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.018 + 0.03 * (t / ride) ** 1.4, location=(x, y, 0.2))
        bpy.ops.object.shade_smooth(); bpy.context.active_object.data.materials.append(gold_m)
    rest = [P(ride + (1 - ride) * j / 20) for j in range(21)]  # still to fly: a fine engraved line
    poly_curve('ahead', [[(x, y + 0.008) for x, y in rest] + [(x, y - 0.008) for x, y in reversed(rest)]], 0.01, 0.004, metal('goldDeep', COL['goldDeep'], 0.3)).location.z = 0.12
    sc = 0.46
    crest = poly_curve('crest', [[((x - CX) * sc, (y - CY) * sc) for x, y in CLOUD],
                                 [((x - CX) * sc, (y - CY) * sc) for x, y in spiral(CX - 0.62, CY + 0.08, 0.3, 1.35, 0.045)],
                                 [((x - CX) * sc, (y - CY) * sc) for x, y in spiral(CX + 0.05, CY + 0.42, 0.34, 1.35, 0.045)],
                                 [((x - CX) * sc, (y - CY) * sc) for x, y in spiral(CX + 0.68, CY - 0.02, 0.28, 1.35, 0.045)]], 0.09, 0.028, gold_m)
    (x0, y0), (x1, y1) = P(ride), P(ride + 0.01)
    crest.location = (x0, y0 + 0.1, 0.16); crest.rotation_euler = (0, 0, math.atan2(y1 - y0, x1 - x0) * 0.8)
    medallion(); jewel_lights()
    camera((0, -2.4, 11), (0, 0, 0), 62)

bpy.ops.render.render(write_still=True)
print('rendered', OUT)
