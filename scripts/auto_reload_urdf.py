#!/usr/bin/env python3
import sys
import os
import time
import subprocess
import signal
import argparse
import tempfile

def get_urdf_content(file_path):
    try:
        # If it's xacro, process it.
        result = subprocess.run(['xacro', file_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error processing Xacro/URDF: {e}")
        print(e.stderr)
        return None

def write_params_yaml(urdf_content, filepath):
    with open(filepath, 'w') as f:
        f.write("/**:\n  ros__parameters:\n    robot_description: |\n")
        for line in urdf_content.split('\n'):
            f.write(f"      {line}\n")

def update_params(urdf_content, params_file):
    if urdf_content is None:
        return

    write_params_yaml(urdf_content, params_file)
    nodes = ['/robot_state_publisher', '/joint_state_publisher_gui']
    
    for node in nodes:
        try:
            # We use subprocess to call 'ros2 param load' to avoid string length limits
            print(f"Updating {node}...")
            subprocess.run(
                ['ros2', 'param', 'load', node, params_file],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
        except Exception as e:
            print(f"Failed to update {node}: {e}")

def stop_process_group(proc, timeout=5.0):
    # Nodes are started via `ros2 run`, which spawns the real node as its own
    # child: signalling only the wrapper would leave the node orphaned, so
    # signal the whole process group (SIGINT first, SIGKILL if it hangs).
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGINT)
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    except ProcessLookupError:
        pass

def main():
    # Treat SIGTERM like Ctrl+C so the finally block below still stops the
    # child nodes instead of leaving them orphaned.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    parser = argparse.ArgumentParser(description='Live URDF Viewer')
    parser.add_argument('file', help='Path to URDF or Xacro file')
    parser.add_argument('--no-rviz', action='store_true', help='Do not launch RViz')
    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"Watching file: {file_path}")
    print("Press Ctrl+C to exit.")

    # 1. Start RViz (optional)
    rviz_process = None
    if not args.no_rviz:
        rviz_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rviz', 'view.rviz')
        rviz_process = subprocess.Popen(['rviz2', '-d', rviz_config],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                        start_new_session=True)

    # 2. Start Nodes ONCE
    urdf_content = get_urdf_content(file_path)
    if urdf_content is None:
        print("Initial URDF parsing failed. Retrying in loop...")
        urdf_content = ""

    # Create temporary parameter file
    fd, params_file = tempfile.mkstemp(suffix='.yaml')
    os.close(fd)
    write_params_yaml(urdf_content, params_file)

    print("Starting ROS nodes...")
    rsp_cmd = [
        'ros2', 'run', 'robot_state_publisher', 'robot_state_publisher',
        '--ros-args', '--params-file', params_file
    ]
    jsp_cmd = [
        'ros2', 'run', 'joint_state_publisher_gui', 'joint_state_publisher_gui',
        '--ros-args', '--params-file', params_file
    ]

    # We use a list to track them
    node_processes = []
    try:
        # Own process group each, so stop_process_group() reaches the real
        # node behind the `ros2 run` wrapper.
        node_processes.append(subprocess.Popen(rsp_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                               start_new_session=True))
        node_processes.append(subprocess.Popen(jsp_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                               start_new_session=True))
    except Exception as e:
        print(f"Failed to start nodes: {e}")
        sys.exit(1)

    last_mtime = os.path.getmtime(file_path)

    try:
        while True:
            try:
                current_mtime = os.path.getmtime(file_path)
                if current_mtime > last_mtime:
                    print("File changed. Updating parameters...")
                    time.sleep(0.1) # Buffer
                    
                    new_content = get_urdf_content(file_path)
                    if new_content:
                        update_params(new_content, params_file)
                        print("Parameters updated.")
                    
                    last_mtime = current_mtime
                
                # Check processes
                if rviz_process and rviz_process.poll() is not None:
                    print("RViz closed. Exiting...")
                    break
                
                # Check if nodes died
                for p in node_processes:
                    if p.poll() is not None:
                        print("A ROS node died unexpectedly.")
                
                time.sleep(1.0)
            except FileNotFoundError:
                time.sleep(1.0)
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        for p in node_processes:
            stop_process_group(p)
        if rviz_process:
            stop_process_group(rviz_process)
        
        # Clean up tmp file
        if os.path.exists(params_file):
            os.remove(params_file)

if __name__ == '__main__':
    main()
