# URDF Visualizer

A standalone ROS 2 package for visualizing any URDF/xacro file, with live
reloading.

## Features

- **Live reloading:** the robot model in RViz updates as soon as you save
  your URDF/xacro file.
- **Generic:** works with any URDF or xacro file path; xacro files are
  expanded automatically.
- **Minimal:** ships a pre-configured RViz view for inspecting links and
  TF frames, with joint sliders from `joint_state_publisher_gui`.
- **Optional physics sandbox:** load the same model in PyBullet with a
  slider per joint.

## Installation

```bash
cd ~/ros2_ws/src
git clone https://github.com/JavideuS/urdf_visualizer.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select urdf_visualizer
source install/setup.bash
```

## Usage

### 1. Live visualizer (recommended)

Launches RViz and watches your URDF/xacro file for changes.

```bash
ros2 launch urdf_visualizer live.launch.py model:=/path/to/your/robot.urdf
```

### 2. Static visualizer

Launches RViz without the auto-reloader, if you just want to look at the
model once.

```bash
ros2 launch urdf_visualizer display.launch.py model:=/path/to/your/robot.urdf
```

Both launch files accept `rvizconfig:=/path/to/config.rviz` to use your
own RViz configuration instead of the bundled one.

### 3. PyBullet sandbox (optional)

Loads the model in PyBullet (fixed base, gravity on) with a position
slider for every revolute/prismatic joint. Needs PyBullet, which is not
installed by rosdep:

```bash
pip install pybullet
ros2 launch urdf_visualizer simulate.launch.py model:=/path/to/your/robot.urdf
```

PyBullet reads plain URDF only: expand xacro files first with
`xacro robot.urdf.xacro -o robot.urdf`.

_Use absolute paths, or paths relative to your current terminal location._

### Using it from your own robot package

Include `live.launch.py` from your package's launch file to get a
one-command viewer for your model:

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory('urdf_visualizer'), 'launch', 'live.launch.py')),
    launch_arguments={'model': model_path, 'rvizconfig': rviz_config}.items(),
)
```

## How it works

- `live.launch.py` runs `rviz2` plus `scripts/auto_reload_urdf.py`, which
  starts `robot_state_publisher` and `joint_state_publisher_gui` and
  watches the model file.
- When the file changes, the script re-expands it and reloads the
  `robot_description` parameter on both nodes (`ros2 param load`, which
  avoids command-line length limits for large models), so RViz updates
  instantly.
- `auto_reload_urdf.py` can also run on its own:
  `scripts/auto_reload_urdf.py robot.urdf` (opens RViz too; add
  `--no-rviz` to skip it).

## License

Apache-2.0
