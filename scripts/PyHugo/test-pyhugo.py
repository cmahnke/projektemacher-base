import sys, os, argparse, logging

sys.path.append(os.path.join(os.path.dirname(__file__)))
from content import Post, Content, Config, Site, Published

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