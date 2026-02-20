import sys, os, argparse, logging
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}/")
print(f"loading from {sys.path[-1]}")
from PyHugo import Post, Content, Config, Site, Published

hugo_dir = "../../../../"
hugo_config = os.path.abspath(os.path.join(os.path.dirname(__file__), hugo_dir))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir", "-b", default=hugo_dir, help="Base directory")
    args = parser.parse_args()

    print(f"Using base directory: {args.basedir}")
    logging.basicConfig(level=logging.DEBUG)
    c = Config(args.basedir)
    print(c.baseURL())