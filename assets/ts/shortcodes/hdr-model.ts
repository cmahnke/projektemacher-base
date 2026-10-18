import * as THREE from 'three/src/Three.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import HDRWebGPURenderer from '@projektemacher/hdr-canvas/three/HDRWebGPURenderer.js';
import WebGPU from '@projektemacher/hdr-canvas/three/WebGPU.js';
import { checkHDRCanvas } from '@projektemacher/hdr-canvas';

declare global {
  interface HTMLCanvasElement {
    scene?: THREE.Scene;
  }
}

let scene: THREE.Scene;
let renderer: THREE.WebGLRenderer | HDRWebGPURenderer;
let camera: THREE.PerspectiveCamera;
let controls: OrbitControls;
let model: THREE.Object3D | undefined;

export function initModel(canvas: HTMLCanvasElement | null, modelUrl: string, _replacements?: unknown): void {
  if (canvas === null) {
    console.log('Model canvas is null!');
    return;
  }

  const loader = new GLTFLoader();
  scene = new THREE.Scene();

  loader.load(modelUrl,
    function (gltf) {
      model = gltf.scene;
      model.traverse((element) => {
        const material = (element as THREE.Mesh).material as THREE.Material | THREE.Material[] | undefined;
        if (material !== undefined && !Array.isArray(material) && material.type !== undefined) {
          const targetMaterial = new THREE.MeshBasicMaterial();
          THREE.MeshBasicMaterial.prototype.copy.call(targetMaterial, material);
          (element as THREE.Mesh).material = targetMaterial;
        }
      });
      model.position.y = -1.0;
      scene.add(model);
    },
    function (_xhr) {
      //console.log( ( _xhr.loaded / _xhr.total * 100 ) + '% loaded' );
    },    function (error) {
      console.log('An error happened', error);
    }
  );

  // Add alpha: true for transparency
  if (WebGPU.isAvailable() && checkHDRCanvas()) {
    renderer = new HDRWebGPURenderer({ canvas: canvas, antialias: true });
  } else {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  }
  const parentWidth = (renderer.domElement.parentNode as HTMLElement).clientWidth;
  const parentHeight = (renderer.domElement.parentNode as HTMLElement).clientHeight;

  camera = new THREE.PerspectiveCamera(40, parentWidth / parentHeight, 0.25, 20);

  camera.position.set(0, 6, 10);
  camera.lookAt(0, 0, 0);

  const ratio = window.devicePixelRatio || 1;
  renderer.setPixelRatio(ratio);

  renderer.setSize(parentWidth, parentHeight);
  renderer.setAnimationLoop(animate);
  renderer.setClearColor(0x000000, 0);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.autoRotate = true;
  controls.autoRotateSpeed = .05;
  controls.minPolarAngle = 0;
  controls.maxPolarAngle = Math.PI * 0.5;
  controls.maxDistance = 18;
  controls.minDistance = 4;

  window.addEventListener("resize", () => {
    const parent = canvas.parentNode as HTMLElement;
    camera.aspect = parent.clientWidth / parent.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(parent.clientWidth, parent.clientHeight);
  });

  canvas.scene = scene;
};

function animate(): void {
  setTimeout(function () {
    requestAnimationFrame(animate);
  }, 1000 / 30);
  //requestAnimationFrame(animate);

  // required if controls.enableDamping or controls.autoRotate are set to true
  controls.update();
  renderer.render(scene, camera);
}

window.initModel = initModel;
