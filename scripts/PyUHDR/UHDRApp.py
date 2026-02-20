import os
import shutil
import logging
import subprocess
import atexit
import tempfile

from PIL import Image
import cv2 as cv
import numpy as np
import docker

docker_image = "ghcr.io/cmahnke/hdr-tools:imagemagick-7.1.1-36-uhdr-main-ffmpeg"
default_ultrahdr_app_bin = "ultrahdr_app"
default_ultrahdr_app_path = f"/usr/local/bin/{default_ultrahdr_app_bin}"


class UHDRApp:
    def __init__(self, debug=False, docker=True, docker_client=None):
        if docker:
            if docker_client is None:
                self.client = UHDRApp.init_docker()
            else:
                self.client = client
        else:
            self.client = None
        self.debug = debug
        if default_ultrahdr_app_bin == "" or (
            not os.path.isfile(default_ultrahdr_app_path) and not os.access(default_ultrahdr_app_path, os.X_OK)
        ):
            self.ultrahdr_app_path = shutil.which(default_ultrahdr_app_bin)
        else:
            self.ultrahdr_app_path = default_ultrahdr_app_path
        if self.ultrahdr_app_path is None:
            logging.error(f"UltraHDR app binary '{default_ultrahdr_app_bin}' not found in PATH or at {default_ultrahdr_app_path}")
            raise FileNotFoundError(f"UltraHDR app binary '{default_ultrahdr_app_bin}' not found in PATH or at {default_ultrahdr_app_path}")
        logging.warning(f"UltraHDR app initialized, binary is at {self.ultrahdr_app_path}")

    def uhdr_process(self, image, gainmap_file, out_file="out.jpeg"):
        if isinstance(image, str):
            with Image.open(image) as img:
                width, height = img.size
            logging.info(f"Loaded file {image}, dimensions {width}x{height}")
        elif isinstance(image, Image.Image):
            logging.warning(f"PIL Image passed to UHDR app wrapper, saving as file - metadata might get lost!")
            width, height = image.size
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False, dir=os.getcwd()) as sdr:
                logging.info(f"Saving PIL Image to {sdr.name}")
                image.save(sdr)
                image = sdr.name
            if not self.debug:
                atexit.register(os.remove, image)
            else:
                logging.info(f"Debug enabled, keeping file {image} after end of program")

        elif isinstance(image, (np.ndarray, np.generic)):
            logging.warning(
                f"NumPy Array (certainly from OpenCV) passed to UHDR app wrapper, saving as file - metadata might get lost!"
            )
            height, width, channels = img.shape
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False, dir=os.getcwd()) as sdr:
                logging.info(f"Saving NumPy Image to {sdr.name}")
                cv.imwrite(sdr.name, image)
                image = sdr.name
            if not self.debug:
                atexit.register(os.remove, image)
            else:
                logging.info(f"Debug enabled, keeping file {image} after end of program")

        else:
            logging.error(f"Can't handle image of type {type(image)}")
            raise ValueError(f"Unknown type {type(image)}")

        logging.info(
            f"Starting processing of input file {image} with gainmap {gainmap_file}, dimensions {width}x{height} to {out_file}"
        )
        if self.client is None:
            return self.uhdr_process_cli(image, gainmap_file, width, height, out_file)
        else:
            return self.uhdr_process_docker(image, gainmap_file, width, height, out_file)

    def uhdr_process_cli(self, input, gainmap_file, width, height, out_file="out.jpeg"):
        args = [
            self.ultrahdr_app_path,
            "-m",
            "0",
            "-p",
            gainmap_file,
            "-i",
            input,
            "-w",
            str(width),
            "-h",
            str(height),
            "-a",
            "0",
            "-z",
            out_file,
        ]
        logging.debug(f"$ {' '.join(args)}")
        subprocess.check_call(args)
        return out_file

    def uhdr_process_docker(self, input_file, gainmap_file, width, height, out_file="out.jpeg"):
        args = [
            default_ultrahdr_app_bin,
            "-m",
            "0",
            "-p",
            gainmap_file,
            "-i",
            input_file,
            "-w",
            str(width),
            "-h",
            str(height),
            "-a",
            "0",
            "-z",
            out_file,
        ]
        logging.debug(f"$ DOCKER {' '.join(args)}")
        self.client.containers.run(
            docker_image,
            args,
            volumes=[f"{os.getcwd()}:{os.getcwd()}"],
            working_dir=os.getcwd(),
        )
        return out_file

    @staticmethod
    def init_docker():
        client = None
        try:
            client = docker.from_env()
            image = docker_image.split("/")
            repo = image.pop(0)
            image = "/".join(image)
            image = image.split(":")
            tag = image.pop(-1)
            logging.warning(f"Pulling {image[0]}, tag {tag} from {repo}")
            local_images =  client.images.list(filters={"reference": f"{repo}/{image[0]}"})
            if len(local_images) < 1:
                client.images.pull(f"{repo}/{image[0]}", tag=tag)
        except:
            logging.warning("Couldn't connect to docker")
        return client
