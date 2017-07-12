from visual import *

xmax = 2.5
scene.range = xmax
initialdistance = xmax/tan(scene.fov/2.0)
box(pos=(-1.5,0,0), color=color.red)
box(pos=(1.5,0,0), color=color.blue)
while 1:
    # Wait while user adjusts the view.
    scene.mouse.getclick()

    # Determine how far we are from the center of the scene.
    savedistance = mag(scene.mouse.camera-scene.center)
    # Keep a copy of current scene.forward.
    saveforward = vector(scene.forward)
    ### Mousing changes scene.forward and can change scene.up too!
    saveup = vector(scene.up)

    # Wait for more mousing, but on the next click, zoom out programatically:
    scene.mouse.getclick()
    # Changing scene.range affects the view (but not vice versa).
    scene.range = 2*scene.range
    savedistance *= scene.range.x/xmax

    # Wait while user changes the view, then restore the saved view.
    scene.mouse.getclick()
    # Determine the new distance from the center.
    distance = mag(scene.mouse.camera-scene.center)
    # Adjust the range based on the new distance.
    scene.range = (savedistance/distance)*xmax
    # Reset the viewing direction.
    scene.up = saveup
    scene.forward = saveforward