# Run in Blender after build_room.build(...) for this kitchen (needs build_room.py exec'd first).
# The builder only places wall cabinets on wall D (x = 0); this kitchen has them on wall B.
# For the renovated scene it also adds what the builder has no types for:
# worktops, splashback, LED strip and pendants (renovation_spec.json > kitchen_extras).
import bpy


def _lin3(c):
    return tuple((v / 255) ** 2.2 for v in c)


def fix_kitchen(scene_name, room_width=3.0, reno=None, cabinet_depth=0.35):
    sc = bpy.data.scenes[scene_name]
    out = []
    for ob in list(sc.objects):
        if ob.name.startswith("wall_cabinets"):
            ob.location.x += room_width - cabinet_depth
            out.append(ob.name)
            key = "black" if ob.name == "wall_cabinets_glass" else ("oak" if "_oak" in ob.name else None)
            if key:
                ob.data.materials.clear(); ob.data.materials.append(mat(key))
    if not reno:
        return out
    extras = reno.get("kitchen_extras", {})
    for key, c in extras.get("custom_materials", {}).items():
        b = mat(key).node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (*_lin3(c["rgb"]), 1)
        b.inputs["Roughness"].default_value = c.get("rough", .5)
        b.inputs["Metallic"].default_value = c.get("metal", 0)
    B = Builder(sc)
    for bx in extras.get("boxes", []):
        B.box(bx["id"], bx["x0"], bx["y0"], bx["z0"], bx["x1"], bx["y1"], bx["z1"], bx["material"], .002)
        out.append(bx["id"])
    H = 3.0
    for p in extras.get("pendants", []):
        top = H - .005; cord = top - (p["globe_y"] + .1)
        B.cyl(p["id"] + "_cord", p["x"], p["globe_y"] + .1 + cord / 2, p["z"], .004, cord, "brass")
        B.cyl(p["id"] + "_cap", p["x"], p["globe_y"] + .12, p["z"], .03, .05, "brass")
        B.cyl(p["id"] + "_globe", p["x"], p["globe_y"], p["z"], .1, .18, "lamp_shade", r2=.1)
        out.append(p["id"])
    return out
