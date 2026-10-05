import bpy
import math
import os
from mathutils import Vector, Matrix


# ============================================================
# USER SETTINGS
# ============================================================

LIVERY_NAME = "test_livery"

OUTPUT_DIR = r"K:\F1C_Livery_Training\renders"

# ------------------------------------------------------------
# TEST MODE
# ------------------------------------------------------------
# True  = 800 x 600
# False = 1920 x 1080
# ------------------------------------------------------------

TEST_MODE = False

if TEST_MODE:
    WIDTH = 800
    HEIGHT = 600
else:
    WIDTH = 1920
    HEIGHT = 1080    
    
SHADOWS = False

# ------------------------------------------------------------
# CAMERA
# ------------------------------------------------------------

CAMERA_NAME = "Camera"

CAMERA_LENS = 55.0


# Extra space around the car.
FRAME_MARGIN = 1.2

REAR_FRAME_MARGIN = 1.5


# ------------------------------------------------------------
# F1 CHALLENGE CAR DIRECTION
# ------------------------------------------------------------
#
# Default F1C car direction:
#
#       FRONT
#         |
#         v
#       -Y
#
# The car longitudinal axis is therefore:
#       (0, -1, 0)
#
# ------------------------------------------------------------

FRONT_DIRECTION = Vector((0.0, -1.0, 0.0))


# ============================================================
# VIEWS
# ============================================================

VIEWS = [
    ("front",           "horizontal", 0),
    ("front34_left",    "horizontal", 45),
    ("side_left",       "horizontal", 90),
    ("rear34_left",     "horizontal", 135),
    ("rear",            "horizontal", 180),
    ("rear34_right",    "horizontal", 225),
    ("side_right",      "horizontal", 270),
    ("front34_right",   "horizontal", 315),

    ("top",             "top",        0),
    ("bottom",          "bottom",     0),
]


# ============================================================
# SCENE
# ============================================================

scene = bpy.context.scene


# ============================================================
# RENDER SETTINGS
# ============================================================

scene.render.resolution_x = WIDTH
scene.render.resolution_y = HEIGHT
scene.render.resolution_percentage = 100

# ------------------------------------------------------------
# PNG + ALPHA
# ------------------------------------------------------------

scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'

# ------------------------------------------------------------
# TRANSPARENT BACKGROUND
# ------------------------------------------------------------

scene.render.film_transparent = True


# ============================================================
# COLOR MANAGEMENT
# ============================================================

try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except:
    pass


# ============================================================
# CAMERA
# ============================================================

camera = bpy.data.objects.get(CAMERA_NAME)

if camera is None:

    camera_data = bpy.data.cameras.new(CAMERA_NAME)

    camera = bpy.data.objects.new(
        CAMERA_NAME,
        camera_data
    )

    bpy.context.collection.objects.link(camera)


camera.data.type = 'PERSP'
camera.data.lens = CAMERA_LENS

camera.data.clip_start = 0.01
camera.data.clip_end = 10000.0

scene.camera = camera


# ============================================================
# FIND SELECTED CAR OBJECTS
# ============================================================

car_objects = [
    obj
    for obj in bpy.context.selected_objects
    if obj.type == 'MESH'
]


if not car_objects:

    raise RuntimeError(
        "No mesh objects selected.\n\n"
        "Select all parts of the car before running the script."
    )


print()
print("==============================================")
print(" F1C LIVERY RENDER")
print("==============================================")
print()
print("Selected mesh objects:")

for obj in car_objects:
    print("  ", obj.name)

print()


# ============================================================
# COLLECT ALL CAR VERTICES
# ============================================================

car_points = []

for obj in car_objects:

    matrix = obj.matrix_world

    for vertex in obj.data.vertices:

        world_position = matrix @ vertex.co

        car_points.append(world_position)


if not car_points:

    raise RuntimeError(
        "Selected mesh objects contain no vertices."
    )


# ============================================================
# CALCULATE CAR WORLD BOUNDS
# ============================================================

min_x = min(point.x for point in car_points)
max_x = max(point.x for point in car_points)

min_y = min(point.y for point in car_points)
max_y = max(point.y for point in car_points)

min_z = min(point.z for point in car_points)
max_z = max(point.z for point in car_points)


car_center = Vector((
    (min_x + max_x) * 0.5,
    (min_y + max_y) * 0.5,
    (min_z + max_z) * 0.5
))


car_size = Vector((
    max_x - min_x,
    max_y - min_y,
    max_z - min_z
))


print("Car center:")
print(car_center)

print()

print("Car size:")
print(car_size)

print()


# ============================================================
# NORMALIZE FRONT DIRECTION
# ============================================================

front_direction = FRONT_DIRECTION.copy()

front_direction.z = 0.0

front_direction.normalize()


# ============================================================
# CAMERA AXES
# ============================================================
#
# Blender camera:
#
# local X = right
# local Y = up
# local -Z = forward
#
# ============================================================

def set_camera_axes(forward, right, up):

    forward = Vector(forward).normalized()
    right = Vector(right).normalized()
    up = Vector(up).normalized()

    # Blender camera local +Z points backwards.
    z_axis = -forward

    # Rebuild an exact orthogonal basis.
    right = up.cross(z_axis).normalized()
    up = z_axis.cross(right).normalized()

    rotation_matrix = Matrix((
        right,
        up,
        z_axis
    )).transposed()

    camera.rotation_euler = rotation_matrix.to_euler()


# ============================================================
# GET CURRENT CAMERA AXES
# ============================================================

def get_camera_axes():

    matrix = camera.matrix_world.to_3x3()

    right = (
        matrix @ Vector((1.0, 0.0, 0.0))
    ).normalized()

    up = (
        matrix @ Vector((0.0, 1.0, 0.0))
    ).normalized()

    forward = (
        matrix @ Vector((0.0, 0.0, -1.0))
    ).normalized()

    return right, up, forward


# ============================================================
# CAMERA FRAMING
# ============================================================

def calculate_distance(frame_margin=FRAME_MARGIN):

    right, up, forward = get_camera_axes()

    horizontal_fov = camera.data.angle_x
    vertical_fov = camera.data.angle_y

    tan_horizontal = math.tan(
        horizontal_fov * 0.5
    )

    tan_vertical = math.tan(
        vertical_fov * 0.5
    )

    required_distance = 0.0

    for point in car_points:

        relative = point - car_center

        x = relative.dot(right)
        y = relative.dot(up)

        depth_offset = relative.dot(-forward)

        required_horizontal = (
            abs(x) / tan_horizontal
            - depth_offset
        )

        required_vertical = (
            abs(y) / tan_vertical
            - depth_offset
        )

        required_distance = max(
            required_distance,
            required_horizontal,
            required_vertical
        )

    required_distance = max(
        required_distance,
        0.001
    )

    required_distance *= frame_margin

    return required_distance


# ============================================================
# POSITION CAMERA
# ============================================================

def position_camera(forward, right, up, frame_margin=FRAME_MARGIN):

    forward = Vector(forward).normalized()
    right = Vector(right).normalized()
    up = Vector(up).normalized()

    set_camera_axes(
        forward,
        right,
        up
    )

    bpy.context.view_layer.update()

    distance = calculate_distance(frame_margin)

    camera.location = (
        car_center
        - forward * distance
    )

    bpy.context.view_layer.update()

    return distance


# ============================================================
# LIGHT CREATION
# ============================================================

def get_or_create_area_light(name):

    light_object = bpy.data.objects.get(name)

    if light_object is not None:

        if light_object.type == 'LIGHT':

            light_object.data.type = 'AREA'

            return light_object


    light_data = bpy.data.lights.new(
        name=name,
        type='AREA'
    )

    light_object = bpy.data.objects.new(
        name,
        light_data
    )

    bpy.context.collection.objects.link(
        light_object
    )

    return light_object


# ============================================================
# LIGHTS
# ============================================================

key_light = get_or_create_area_light(
    "Livery_Key_Light"
)

fill_light = get_or_create_area_light(
    "Livery_Fill_Light"
)

rim_light = get_or_create_area_light(
    "Livery_Rim_Light"
)

bottom_light = get_or_create_area_light(
    "Livery_Bottom_Fill"
)


# ============================================================
# LIGHT PARAMETERS
# ============================================================

key_light.data.energy = 1400
key_light.data.shape = 'DISK'
key_light.data.size = 5.0
key_light.data.use_shadow = SHADOWS

fill_light.data.energy = 700
fill_light.data.shape = 'DISK'
fill_light.data.size = 5.0
fill_light.data.use_shadow = SHADOWS

rim_light.data.energy = 1000
rim_light.data.shape = 'DISK'
rim_light.data.size = 4.0
rim_light.data.use_shadow = SHADOWS

bottom_light.data.energy = 1400
bottom_light.data.shape = 'DISK'
bottom_light.data.size = 5.0
bottom_light.data.use_shadow = SHADOWS


# ============================================================
# LOOK AT OBJECT
# ============================================================

def look_at(obj, target):

    direction = (
        Vector(target)
        - obj.location
    ).normalized()

    obj.rotation_euler = direction.to_track_quat(
        '-Z',
        'Y'
    ).to_euler()


# ============================================================
# CAMERA-RELATIVE LIGHTING
# ============================================================

def setup_lighting(is_bottom_view=False):

    right, up, forward = get_camera_axes()

    # Scale lights according to car size.
    light_scale = max(
        car_size.x,
        car_size.y,
        car_size.z
    )


    # --------------------------------------------------------
    # KEY
    # --------------------------------------------------------

    key_position = (
        car_center
        + right * light_scale * 0.9
        + up * light_scale * 1.5
        + forward * light_scale * 1.0
    )

    key_light.location = key_position

    key_light.data.energy = (
        1000
        if is_bottom_view
        else 1400
    )

    key_light.data.size = (
        light_scale * 0.8
    )

    look_at(
        key_light,
        car_center
    )


    # --------------------------------------------------------
    # FILL
    # --------------------------------------------------------

    fill_position = (
        car_center
        - right * light_scale * 1.3
        + up * light_scale * 0.7
        + forward * light_scale * 0.5
    )

    fill_light.location = fill_position

    fill_light.data.energy = (
        1000
        if is_bottom_view
        else 700
    )

    fill_light.data.size = (
        light_scale * 0.8
    )

    look_at(
        fill_light,
        car_center
    )


    # --------------------------------------------------------
    # RIM
    # --------------------------------------------------------

    rim_position = (
        car_center
        - forward * light_scale * 1.5
        + up * light_scale * 1.0
    )

    rim_light.location = rim_position

    rim_light.data.energy = (
        800
        if is_bottom_view
        else 1000
    )

    rim_light.data.size = (
        light_scale * 0.7
    )

    look_at(
        rim_light,
        car_center
    )


    # --------------------------------------------------------
    # BOTTOM LIGHT
    # --------------------------------------------------------

    if is_bottom_view:

        bottom_position = (
            car_center
            + Vector((0.0, 0.0, -1.0))
            * light_scale
            * 1.0
            + right
            * light_scale
            * 0.2
        )

        bottom_light.location = bottom_position

        bottom_light.data.energy = 1400

        bottom_light.data.size = (
            light_scale * 0.8
        )

        bottom_light.hide_render = False

        look_at(
            bottom_light,
            car_center
        )

    else:

        bottom_light.data.energy = 0

        bottom_light.hide_render = True


# ============================================================
# HORIZONTAL VIEW
# ============================================================

def set_horizontal_view(angle_degrees):

    angle = math.radians(
        angle_degrees
    )


    # Rotate the F1C front direction around Z.
    direction = Vector((

        front_direction.x
        * math.cos(angle)
        -
        front_direction.y
        * math.sin(angle),

        front_direction.x
        * math.sin(angle)
        +
        front_direction.y
        * math.cos(angle),

        0.0
    ))

    direction.normalize()


    # Camera looks toward the car.
    forward = -direction


    # World vertical.
    up = Vector((
        0.0,
        0.0,
        1.0
    ))


    # Camera right.
    right = up.cross(
        forward
    ).normalized()
    
    if angle_degrees == 180:
        frame_margin = REAR_FRAME_MARGIN
    else:
        frame_margin = FRAME_MARGIN

    distance = position_camera(
        forward,
        right,
        up,
        frame_margin
    )


    setup_lighting(
        False
    )


    return distance


# ============================================================
# TOP VIEW
# ============================================================

def set_top_view():

    # Camera looks straight down.
    forward = Vector((
        0.0,
        0.0,
        -1.0
    ))


    # IMPORTANT:
    #
    # Camera local X points along the car's
    # longitudinal axis.
    #
    # This makes the car horizontal in the image.
    #

    right = front_direction.copy()

    right.z = 0.0

    right.normalize()


    # Build camera vertical axis.
    up = (
        (-forward)
        .cross(right)
        .normalized()
    )


    distance = position_camera(
        forward,
        right,
        up
    )


    # Explicitly restore axes.
    # Do NOT use look_at() here.
    set_camera_axes(
        forward,
        right,
        up
    )

    bpy.context.view_layer.update()


    setup_lighting(
        False
    )


    return distance


# ============================================================
# BOTTOM VIEW
# ============================================================

def set_bottom_view():

    # Camera looks straight upward.
    forward = Vector((
        0.0,
        0.0,
        1.0
    ))


    # Keep the car longitudinal axis horizontal.
    right = front_direction.copy()

    right.z = 0.0

    right.normalize()


    # Build camera vertical axis.
    up = (
        (-forward)
        .cross(right)
        .normalized()
    )


    distance = position_camera(
        forward,
        right,
        up
    )


    # Explicitly restore axes.
    # Do NOT use look_at() here.
    set_camera_axes(
        forward,
        right,
        up
    )

    bpy.context.view_layer.update()


    setup_lighting(
        True
    )


    return distance


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

output_folder = os.path.join(
    OUTPUT_DIR,
    LIVERY_NAME
)

os.makedirs(
    output_folder,
    exist_ok=True
)


# ============================================================
# SAVE ORIGINAL CAMERA TRANSFORM
# ============================================================

original_camera_location = camera.location.copy()

original_camera_rotation = camera.rotation_euler.copy()

original_camera_scale = camera.scale.copy()


# ============================================================
# RENDER ALL VIEWS
# ============================================================

print()
print("==============================================")
print(" STARTING RENDER")
print("==============================================")
print()

for view_name, view_type, angle in VIEWS:

    print(
        "Rendering:",
        view_name
    )


    # --------------------------------------------------------
    # SET CAMERA
    # --------------------------------------------------------

    if view_type == "horizontal":

        distance = set_horizontal_view(
            angle
        )

    elif view_type == "top":

        distance = set_top_view()

    elif view_type == "bottom":

        distance = set_bottom_view()

    else:

        raise RuntimeError(
            "Unknown view type: "
            + str(view_type)
        )


    bpy.context.view_layer.update()


    # --------------------------------------------------------
    # OUTPUT FILE
    # --------------------------------------------------------

    filename = (
        f"{LIVERY_NAME}_{view_name}.png"
    )

    filepath = os.path.join(
        output_folder,
        filename
    )


    scene.render.filepath = filepath


    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    bpy.ops.render.render(
        write_still=True
    )


    print(
        "  Saved:",
        filepath
    )

    print(
        "  Camera distance:",
        round(distance, 4)
    )

    print()


# ============================================================
# RESTORE CAMERA
# ============================================================

camera.location = (
    original_camera_location
)

camera.rotation_euler = (
    original_camera_rotation
)

camera.scale = (
    original_camera_scale
)


# ============================================================
# FINISHED
# ============================================================

print()
print("==============================================")
print(" RENDER COMPLETE")
print("==============================================")
print()
print("Livery:")
print(
    " ",
    LIVERY_NAME
)

print()

print("Output:")
print(
    " ",
    output_folder
)

print()

print("Resolution:")
print(
    " ",
    WIDTH,
    "x",
    HEIGHT
)

print()

print("Transparent background:")
print(
    " ",
    scene.render.film_transparent
)

print()

print("Views rendered:")

for view_name, _, _ in VIEWS:

    print(
        "  ",
        view_name
    )

print()
print("==============================================")