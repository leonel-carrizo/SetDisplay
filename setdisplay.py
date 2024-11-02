import argparse
from config import manager, loader

def main():
    parser = argparse.ArgumentParser(description="SetDisplay: Manage monitor configurations")
    parser.add_argument('--save', help="Save the current monitor configuration", action="store_true")
    parser.add_argument('--apply', help="Apply a saved monitor configuration", action="store_true")
    parser.add_argument('--profile', help="Specify the profile name (default is 'default')", default="default")
    args = parser.parse_args()

    if args.save:
        monitors = manager.get_monitor_properties()
        manager.save_monitor_configuration(monitors, args.profile)
    elif args.apply:
        config = loader.load_monitor_configuration(args.profile)
        loader.apply_monitor_configuration(config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

