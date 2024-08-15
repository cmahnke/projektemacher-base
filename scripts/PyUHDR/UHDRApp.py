import os
import shutil
import logging
import subprocess
import atexit

from PIL import Image
import docker

docker_image = 'ghcr.io/cmahnke/hdr-tools:imagemagick-7.1.1-36-uhdr-main-ffmpeg'
default_ultrahdr_app_bin = 'ultrahdr_app'
default_ultrahdr_app_path = f"/usr/local/bin/{default_ultrahdr_app_bin}"

class UHDRApp:
    def __init__(self):
        self.init()

        if default_ultrahdr_app_bin == '' or (not os.path.isfile(default_ultrahdr_app_path) and not os.access(default_ultrahdr_app_path, os.X_OK)):
            self.ultrahdr_app_path = shutil.which(default_ultrahdr_app_bin)
        else:
            self.ultrahdr_app_path = default_ultrahdr_app_path
        logging.warning(f"UltraHDR app initialized, binary is at {self.ultrahdr_app_path}")

    def init(self):
        try:
            self.client = docker.from_env()
            image = docker_image.split("/")
            repo = image.pop(0)
            image = "/".join(image)
            image = image.split(":")
            tag = image.pop(-1)
            logging.warning(f"Pulling {image[0]}, tag {tag} from {repo}")
            self.client.images.pull(f"{repo}/{image[0]}", tag=tag)

        except:
            self.client = None
            logging.warning("Couldn't connect to docker")

    def uhdr_process(self, image, gainmap_file, out_file="out.jpeg"):
        if isinstance(image, str):
            img = Image.open(image)
            width, height = img.size
        elif isinstance(image, Image):
            width, height = img.size
            with tempfile.NamedTemporaryFile(mode="wb") as sdr:
                image.save(sdr)
                image = sdr.name
            atexit.register(os.remove, image)
        elif isinstance(image, (np.ndarray, np.generic)):
            height, width, channels = img.shape
            raise

        if self.client is None:
            return self.uhdr_process_cli(image, gainmap_file, width, height, out_file)
        else:
            return self.uhdr_process_docker(image, gainmap_file, width, height, out_file)

    def uhdr_process_cli(self, input, gainmap_file, width, height, out_file="out.jpeg"):
        args = [self.ultrahdr_app_path, "-m", "0", "-p", gainmap_file, "-i", input, "-w", str(width), "-h", str(height), "-a", "0", "-z", out_file]
        logging.debug(f"$ {' '.join(args)}")
        subprocess.check_call(args)
        return out_file

    def uhdr_process_docker(self, input, gainmap_file, width, height, out_file="out.jpeg"):
        args = [default_ultrahdr_app_bin, "-m", "0", "-p", gainmap_file, "-i", input, "-w", str(width), "-h", str(height), "-a", "0", "-z", out_file]
        logging.debug(f"$ {' '.join(args)}")
        self.client.containers.run(docker_image, args, volumes=[f"{os.getcwd()}:{os.getcwd()}"], working_dir=os.getcwd())
        return out_file
